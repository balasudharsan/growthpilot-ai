from models.business_input import BusinessInput
from services.classifier import classify_business
from utils.logger import get_logger
from utils.sanitiser import sanitise_payload


logger = get_logger(__name__)


def build_business_payload(data: BusinessInput) -> dict:
    try:
        clean_payload = sanitise_payload(data.model_dump())
        clean_payload["classification"] = classify_business(data)
        return clean_payload
    except Exception:
        logger.exception("Failed to build clean business payload")
        raise
