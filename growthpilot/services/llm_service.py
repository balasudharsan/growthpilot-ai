import json
import os
import time

from groq import Groq

from utils.config import load_project_env
from utils.logger import get_logger
from utils.validator import LLMStrategyOutput, validate_llm_output


load_project_env()
logger = get_logger(__name__)


def _fallback_strategy(payload: dict) -> dict:
    details = payload["business_details"]
    goals = payload["growth_goals"]
    return {
        "executive_summary": (
            f"{details['business_name']} should focus on a practical growth plan for "
            f"{details['industry']} with priority on {goals['primary_goal']}."
        ),
        "swot": {
            "strengths": [payload["competition"]["competitive_advantage"]],
            "weaknesses": payload["problems"]["biggest_challenges"][:3],
            "opportunities": ["Improve channel focus", "Increase repeat purchases", "Clarify pricing tiers"],
            "threats": payload["competition"]["main_competitors"][:3] or ["Competitive pressure"],
        },
        "pricing_recommendations": [
            "Review product-level margins before changing prices.",
            "Bundle best sellers with complementary offers.",
            "Test a premium package for high-intent customers.",
        ],
        "marketing_plan": [
            "Double down on the strongest current channel.",
            "Create weekly customer proof content.",
            "Build a simple lead capture and follow-up sequence.",
        ],
        "thirty_day_action_plan": [
            "Audit sales, margin, and channel data.",
            "Interview five recent customers.",
            "Launch one offer test and one channel test.",
            "Review results and scale the better-performing experiment.",
        ],
        "risks": ["Plan generated without live LLM because GROQ_API_KEY is not configured."],
    }


def generate_strategy(payload: dict) -> LLMStrategyOutput:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        logger.warning("GROQ_API_KEY missing; using validated fallback strategy")
        return validate_llm_output(_fallback_strategy(payload))

    client = Groq(api_key=api_key)
    prompt = (
        "You are GrowthPilot AI. Return ONLY valid JSON. "
        "All array fields must contain STRINGS only -- "
        "never objects or dicts inside arrays. "
        "Required JSON schema:\n"
        "{\n"
        '  "executive_summary": "string",\n'
        '  "swot": {\n'
        '    "strengths": ["string", "string"],\n'
        '    "weaknesses": ["string", "string"],\n'
        '    "opportunities": ["string", "string"],\n'
        '    "threats": ["string", "string"]\n'
        '  },\n'
        '  "pricing_recommendations": ["string", "string"],\n'
        '  "marketing_plan": ["string", "string"],\n'
        '  "thirty_day_action_plan": ["string", "string"],\n'
        '  "risks": ["string", "string"]\n'
        "}\n"
        "IMPORTANT: Every item in every array must be a "
        "plain string sentence. Never use objects inside "
        "arrays. Example correct format:\n"
        '"pricing_recommendations": ['
        '"Offer bundle deals to increase average order value",'
        '"Test a premium tier for loyal customers"]\n'
        f"Business data: {json.dumps(payload, ensure_ascii=True)}"
    )

    retry_waits = {1: 2, 2: 5}
    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a concise business growth strategy analyst."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                timeout=30,
            )
            raw_content = response.choices[0].message.content or "{}"
            return validate_llm_output(json.loads(raw_content))
        except Exception:
            if attempt < 3:
                wait_seconds = retry_waits[attempt]
                logger.warning(
                    "Groq strategy generation failed on attempt %s; retrying attempt %s after %s seconds",
                    attempt,
                    attempt + 1,
                    wait_seconds,
                    exc_info=True,
                )
                time.sleep(wait_seconds)
                continue

            logger.exception("Groq strategy generation failed after 3 attempts")
            logger.warning("Falling back to template strategy due to LLM failure")
            return validate_llm_output(_fallback_strategy(payload))
