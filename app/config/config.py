import os

from dotenv import load_dotenv

from app.utils.log import logger

load_dotenv()


def get_secret(secret_name, default_value: str = ""):
    try:
        value = os.environ.get(secret_name, default_value)
        return value if value is not None else default_value
    except Exception:
        logger.error("Error getting secret: %s", secret_name)
        return default_value


# MongoDB Configuration
MONGO_URI = get_secret("MONGO_URI", "")
DATABASE_NAME = get_secret("DATABASE_NAME", "copilot")

# Claude Configs
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# LangChain Configuration
LANGCHAIN_TRACING = get_secret("LANGCHAIN_TRACING", "false") == "true"
LANGCHAIN_API_KEY = get_secret("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = get_secret("LANGCHAIN_PROJECT", "financial_agent")
LANGCHAIN_ENDPOINT = get_secret("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

JWT_SECRET = get_secret("JwtSecret")
ENVIRONMENT = get_secret("Environment")
PORT = get_secret("PORT", "8000")