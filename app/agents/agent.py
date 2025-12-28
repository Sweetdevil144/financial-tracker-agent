from langchain.agents import create_agent
class Agent:
    def __init__(self):
        pass
    
    async def parse_expense(self, user_text):
        pass
    
    async def process_expense(self, parsed_data):
        pass
        
#   User Input (raw text)                                                                                                                                                                                      
#       ↓                                                                                                                                                                                                      
#   [AI Agent 1: Parser/Extractor]                                                                                                                                                                             
#       ↓ (structured JSON)                                                                                                                                                                                    
#   {amount, currency, date, merchant, category, ...}                                                                                                                                                          
#       ↓                                                                                                                                                                                                      
#   [AI Agent 2: Processor/Validator]                                                                                                                                                                          
#       ↓                                                                                                                                                                                                      
#   Database Storage + Response 