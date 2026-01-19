from typing import Any, Type

from langchain.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from pydantic import BaseModel, SecretStr

from app.config import config
from app.utils.log import logger


class LLMService:
    def __init__(self):
        self.api_key = config.ANTHROPIC_API_KEY
        if not self.api_key:
            logger.error("No API KEY detected. Closing agent connection")
            return

        self.db_name = config.DATABASE_NAME
        self.db_url = config.MONGO_URI
        self.agent = ChatAnthropic(
            model_name="claude-sonnet-4-20250514",
            api_key=SecretStr(self.api_key),
            temperature=0.7,
            max_retries=2,
            timeout=60,
            stop=None,
            max_tokens_to_sample=4096
        )

    async def chat(
        self, user_messages: str, system_prompt: str, response_format=None
    ) -> AIMessage:
        system_msg = SystemMessage(system_prompt)
        human_msg = HumanMessage(user_messages)
        messages = [system_msg, human_msg]

        res = await self.agent.ainvoke(messages)

        return res

    async def parse_structured(
        self, user_prompt: str, system_prompt: str, output_schema: Type[BaseModel]
    ) -> dict[str, Any]:
        system_msg = SystemMessage(system_prompt)
        human_msg = HumanMessage(user_prompt)
        messages = [system_msg, human_msg]
        res = await self.agent.with_structured_output(output_schema).ainvoke(messages)
        return res
