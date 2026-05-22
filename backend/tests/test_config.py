from app.core.config import get_settings, parse_bool
from app.db.config import get_database_url


def test_parse_bool_handles_common_values():
    assert parse_bool("true") is True
    assert parse_bool("YES") is True
    assert parse_bool("0") is False
    assert parse_bool(None, default=True) is True


def test_settings_do_not_require_ai_secret_for_local_startup():
    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ai_provider == "openai-compatible"
    assert settings.ai_api_key is None


def test_database_url_placeholder_is_available():
    get_settings.cache_clear()

    assert get_database_url().startswith("postgresql+psycopg://")
