import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ReplayProtectionConfig:
    enabled: bool = True
    nonce_ttl_seconds: int = 300


@dataclass(frozen=True)
class AppConfig:
    app_id: str
    replay_protection: ReplayProtectionConfig


def load_config() -> AppConfig:
    app_id = os.environ.get("TEST_APP_ID", "rafael-ai-office-test")
    if not app_id.strip():
        raise ValueError("TEST_APP_ID must not be empty")

    enabled_value = os.environ.get("C02_REPLAY_PROTECTION_ENABLED", "true").lower()
    if enabled_value not in {"true", "false"}:
        raise ValueError("C02_REPLAY_PROTECTION_ENABLED must be 'true' or 'false'")

    ttl_value = os.environ.get("C02_NONCE_TTL_SECONDS", "300")
    try:
        nonce_ttl_seconds = int(ttl_value)
    except ValueError as error:
        raise ValueError("C02_NONCE_TTL_SECONDS must be an integer") from error
    if nonce_ttl_seconds <= 0:
        raise ValueError("C02_NONCE_TTL_SECONDS must be positive")

    return AppConfig(
        app_id=app_id,
        replay_protection=ReplayProtectionConfig(
            enabled=enabled_value == "true",
            nonce_ttl_seconds=nonce_ttl_seconds,
        ),
    )
