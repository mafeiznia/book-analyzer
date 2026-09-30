"""Provider manager: loads built-in + custom providers, holds active state."""
import json
import os

from providers.base import LLMProvider
from providers.custom import CustomProvider
from providers.registry import BUILTIN
from storage.db import get_connection


class ProviderManager:
    def __init__(self) -> None:
        self.providers: dict[str, LLMProvider] = {}
        self.active: str | None = None

    # --- Loading ---
    def load(self) -> None:
        """Seed built-ins if missing, then load all providers from DB."""
        self.providers.clear()
        self.active = None

        with get_connection() as conn:
            # Seed built-ins
            for name, cls in BUILTIN.items():
                exists = conn.execute(
                    "SELECT id FROM providers WHERE name=?", (name,)
                ).fetchone()
                if not exists:
                    conn.execute(
                        """INSERT INTO providers
                           (name, base_url, env_key, api_key, is_builtin, is_active, models)
                           VALUES (?, ?, ?, '', 1, 0, ?)""",
                        (name, cls.base_url, cls.env_key, json.dumps(cls.default_models)),
                    )
            conn.commit()

            rows = conn.execute("SELECT * FROM providers").fetchall()

        for row in rows:
            name = row["name"]
            env_key = row["env_key"] or ""
            db_key = (row["api_key"] or "").strip()
            env_value = os.getenv(env_key, "").strip() if env_key else ""

            # Priority: DB value > .env value
            api_key = db_key if db_key else env_value

            if row["is_builtin"]:
                cls = BUILTIN.get(name)
                if cls is None:
                    continue
                provider = cls(api_key=api_key, models=list(cls.default_models))
            else:
                models = json.loads(row["models"]) if row["models"] else []
                provider = CustomProvider(
                    name=name,
                    label=name,
                    base_url=row["base_url"] or "",
                    env_key=env_key,
                    api_key=api_key,
                    models=models,
                )
            self.providers[name] = provider

            if row["is_active"]:
                self.active = name

        # Fallback active
        if not self.active and self.providers:
            default = os.getenv("DEFAULT_PROVIDER", "").strip()
            chosen = default if default in self.providers else next(iter(self.providers))
            self.set_active(chosen)

    # --- Queries ---
    def list_providers(self) -> list[dict]:
        """Return list of dicts for UI (without API keys)."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM providers ORDER BY is_builtin DESC, name"
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            provider = self.providers.get(d["name"])
            d["has_key"] = provider.has_key if provider else False
            d["models_list"] = json.loads(d["models"]) if d["models"] else []
            d["key_source"] = self._key_source(d)
            result.append(d)
        return result

    @staticmethod
    def _key_source(row: dict) -> str:
        """Determine where the current API key comes from."""
        if (row.get("api_key") or "").strip():
            return "db"
        env_key = row.get("env_key") or ""
        if env_key and os.getenv(env_key, "").strip():
            return "env"
        return "none"

    def get(self, name: str) -> LLMProvider | None:
        return self.providers.get(name)

    def get_active(self) -> LLMProvider | None:
        return self.providers.get(self.active) if self.active else None

    def get_raw(self, name: str) -> dict | None:
        """Return the raw DB row for editing purposes."""
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM providers WHERE name=?", (name,)
            ).fetchone()
        return dict(row) if row else None

    # --- Mutations ---
    def set_active(self, name: str) -> None:
        if name not in self.providers:
            return
        with get_connection() as conn:
            conn.execute("UPDATE providers SET is_active=0")
            conn.execute("UPDATE providers SET is_active=1 WHERE name=?", (name,))
            conn.commit()
        self.active = name

    def add_custom(
        self,
        name: str,
        base_url: str,
        env_key: str,
        models: list[str],
        api_key: str = "",
    ) -> None:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO providers
                   (name, base_url, env_key, api_key, is_builtin, is_active, models)
                   VALUES (?, ?, ?, ?, 0, 0, ?)""",
                (name, base_url, env_key, api_key.strip(), json.dumps(models)),
            )
            conn.commit()
        self.load()

    def update_provider(
        self,
        name: str,
        api_key: str | None = None,
        models: list[str] | None = None,
        env_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Update a provider's editable fields."""
        with get_connection() as conn:
            row = conn.execute(
                "SELECT is_builtin FROM providers WHERE name=?", (name,)
            ).fetchone()
            if row is None:
                return
            is_builtin = row["is_builtin"]

            sets = []
            values = []

            if api_key is not None:
                sets.append("api_key=?")
                values.append(api_key.strip())
            if models is not None:
                sets.append("models=?")
                values.append(json.dumps(models))
            # env_key and base_url only editable for custom providers
            if not is_builtin:
                if env_key is not None:
                    sets.append("env_key=?")
                    values.append(env_key.strip())
                if base_url is not None:
                    sets.append("base_url=?")
                    values.append(base_url.strip())

            if not sets:
                return

            values.append(name)
            conn.execute(
                f"UPDATE providers SET {', '.join(sets)} WHERE name=?",
                values,
            )
            conn.commit()
        self.load()

    def remove_custom(self, name: str) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM providers WHERE name=? AND is_builtin=0", (name,))
            conn.commit()
        self.load()


provider_manager = ProviderManager()