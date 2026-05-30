from templates.strategy_templates import (
    MARKETING_TEMPLATE,
    PRICING_TEMPLATE,
    SWOT_TEMPLATE,
    THIRTY_DAY_TEMPLATE,
)
from utils.logger import get_logger


logger = get_logger(__name__)


def load_strategy_templates() -> dict:
    try:
        return {
            "swot": SWOT_TEMPLATE,
            "pricing": PRICING_TEMPLATE,
            "marketing": MARKETING_TEMPLATE,
            "thirty_day": THIRTY_DAY_TEMPLATE,
        }
    except Exception:
        logger.exception("Failed to load strategy templates")
        raise
