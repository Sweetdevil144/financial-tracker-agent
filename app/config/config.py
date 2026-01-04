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

# Azure OpenAI Configuration
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = get_secret("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = get_secret("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = get_secret("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = get_secret("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# LangChain Configuration
LANGCHAIN_TRACING = get_secret("LANGCHAIN_TRACING", "false") == "true"
LANGCHAIN_API_KEY = get_secret("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = get_secret("LANGCHAIN_PROJECT", "cortex-agent-service")
LANGCHAIN_ENDPOINT = get_secret("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
