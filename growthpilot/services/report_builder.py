from datetime import datetime, timezone
from uuid import uuid4

from utils.logger import get_logger
from utils.validator import LLMStrategyOutput


logger = get_logger(__name__)


def build_report(input_id: int, payload: dict, strategy: LLMStrategyOutput, templates: dict) -> dict:
    try:
        return {
            "report_id": str(uuid4()),
            "input_id": input_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "business": payload["business_details"],
            "classification": payload["classification"],
            "executive_summary": strategy.executive_summary,
            "swot": strategy.swot or templates["swot"],
            "pricing_recommendations": strategy.pricing_recommendations or templates["pricing"],
            "marketing_plan": strategy.marketing_plan or templates["marketing"],
            "thirty_day_action_plan": strategy.thirty_day_action_plan or templates["thirty_day"],
            "risks": strategy.risks,
        }
    except Exception:
        logger.exception("Failed to build report")
        raise
