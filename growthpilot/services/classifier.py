from models.business_input import BusinessInput
from utils.logger import get_logger


logger = get_logger(__name__)


def classify_business(data: BusinessInput) -> dict[str, str]:
    try:
        revenue = data.sales.monthly_revenue
        stage = data.business_details.business_stage

        if revenue < 10000:
            tier = "early"
        elif revenue < 100000:
            tier = "growth"
        else:
            tier = "scale"

        business_type = f"{stage}_{data.business_details.industry.lower().replace(' ', '_')}"
        return {"business_type": business_type, "tier": tier}
    except Exception:
        logger.exception("Business classification failed")
        raise
