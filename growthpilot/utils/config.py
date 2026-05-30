import logging
import os
from pathlib import Path

from dotenv import load_dotenv


logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"


def load_project_env() -> None:
    # .env is at growthpilot/.env
    # config.py is at growthpilot/utils/config.py
    # So go up TWO levels from this file to find .env
    env_path = Path(__file__).parent.parent / ".env"
    logger.info(f"Loading .env from: {env_path}")
    load_dotenv(env_path)
    logger.info(f"DATABASE_URL loaded: {'YES' if os.getenv('DATABASE_URL') else 'NO'}")


def project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return BASE_DIR / path
