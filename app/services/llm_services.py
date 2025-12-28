from app.config import config
from langchain_openai import AzureChatOpenAI
from langchain.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

class LLMService:
    def __init__(self):
        self.deployment_name = config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        self.model = config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        self.api_key = config.AZURE_OPENAI_API_KEY
        self.api_version = config.AZURE_OPENAI_API_VERSION
        self.chat_endpoint = config.AZURE_OPENAI_ENDPOINT
        self.db_name = config.DATABASE_NAME
        self.db_url = config.MONGO_URI
        self.agent = AzureChatOpenAI(
            name = self.deployment_name,
            model = self.model,
            api_key = SecretStr(self.api_key),
            azure_endpoint = self.chat_endpoint,
            api_version = self.api_version,
            verbose = True,
            temperature = 0.7,
            max_retries = 2,
            reasoning={
                "effort": "medium",  # Can be "low", "medium", or "high"
                "summary": "auto",  # Can be "auto", "concise", or "detailed"
            }
            # Future params TBD
        )
    
    async def chat(self, user_messages: str, system_prompt, response_format = None):
        system_msg = SystemMessage(system_prompt)
        human_msg = HumanMessage(user_messages)
        messages = [system_msg, human_msg]
        
        if response_format:
            res = await self.agent.with_structured_output(response_format).ainvoke(messages)
        else:
            res = await self.agent.ainvoke(messages)
        
        return res
    
    async def parse_structured(self, user_text, system_prompt, output_schema):
        system_msg = SystemMessage(system_prompt)
        human_msg = HumanMessage(user_text)
        messages = [system_msg, human_msg]
        
        res = await self.agent.with_structured_output(output_schema).ainvoke(messages)
        
        return res