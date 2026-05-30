from typing import Any

from pydantic import BaseModel, Field, ValidationError

from utils.logger import get_logger


logger = get_logger(__name__)


class LLMStrategyOutput(BaseModel):
    executive_summary: str = Field(..., min_length=20, max_length=2000)
    swot: dict[str, list[str]] = Field(...)
    pricing_recommendations: list[str] = Field(..., min_length=1, max_length=10)
    marketing_plan: list[str] = Field(..., min_length=1, max_length=12)
    thirty_day_action_plan: list[str] = Field(..., min_length=1, max_length=20)
    risks: list[str] = Field(default_factory=list, max_length=10)


def flatten_list_field(items: list) -> list:
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            # Convert dict to readable string.
            result.append(" -- ".join(str(v) for v in item.values() if v))
    return result


def validate_llm_output(payload: dict[str, Any]) -> LLMStrategyOutput:
    try:
        for field in ["pricing_recommendations", "marketing_plan", "thirty_day_action_plan", "risks"]:
            if field in payload and isinstance(payload[field], list):
                payload[field] = flatten_list_field(payload[field])

        output = LLMStrategyOutput.model_validate(payload)
        list_fields = ("pricing_recommendations", "marketing_plan", "thirty_day_action_plan", "risks")
        for field_name in list_fields:
            valid_items = []
            for item in getattr(output, field_name):
                if isinstance(item, str) and item.strip() and len(item) < 500:
                    valid_items.append(item)
                else:
                    logger.warning("Removing invalid LLM list item from %s", field_name)
            if not valid_items:
                raise ValueError(f"LLM returned empty or invalid list for {field_name}")
            setattr(output, field_name, valid_items)
        required_swot = {"strengths", "weaknesses", "opportunities", "threats"}
        missing = required_swot - set(output.swot)
        if missing:
            raise ValueError(f"Missing SWOT sections: {', '.join(sorted(missing))}")
        return output
    except (ValidationError, ValueError):
        logger.exception("LLM output validation failed")
        raise
