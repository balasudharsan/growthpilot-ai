import html
import re
from typing import Any

from utils.logger import get_logger


logger = get_logger(__name__)

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WHITESPACE = re.compile(r"\s+")
PROMPT_INJECTION_PATTERNS = re.compile(
    r"ignore all previous instructions|you are now|forget your instructions|"
    r"disregard the above|new instruction:|system prompt:|act as|jailbreak",
    re.IGNORECASE,
)


def block_injection_patterns(value: str) -> str:
    return PROMPT_INJECTION_PATTERNS.sub("[REMOVED]", value)


def sanitise_text(value: str, field_name: str | None = None) -> str:
    try:
        cleaned = html.escape(value.strip(), quote=False)
        if PROMPT_INJECTION_PATTERNS.search(cleaned):
            if field_name:
                logger.warning("Prompt injection pattern detected in field '%s'", field_name)
            else:
                logger.warning("Prompt injection pattern detected during sanitisation")
        cleaned = block_injection_patterns(cleaned)
        cleaned = CONTROL_CHARS.sub("", cleaned)
        cleaned = WHITESPACE.sub(" ", cleaned)
        return cleaned[:3000]
    except Exception:
        logger.exception("Failed to sanitise text")
        return ""


def sanitise_payload(value: Any, field_name: str | None = None) -> Any:
    try:
        if isinstance(value, str):
            return sanitise_text(value, field_name=field_name)
        if isinstance(value, list):
            return [sanitise_payload(item, field_name=field_name) for item in value]
        if isinstance(value, dict):
            return {key: sanitise_payload(item, field_name=str(key)) for key, item in value.items()}
        return value
    except Exception:
        logger.exception("Failed to sanitise payload")
        return value
