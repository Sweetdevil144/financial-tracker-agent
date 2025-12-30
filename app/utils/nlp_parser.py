def extract_amount(text: str):
    """
    Examples to handle:                                                                                                                                                                                        
      - "spent $50 on groceries" → 50.0                                                                                                                                                                          
      - "bought coffee for 4.50" → 4.50                                                                                                                                                                          
      - "paid fifty dollars" → 50.0 (word to number)                                                                                                                                                             
      - "1,250.99 for rent" → 1250.99 
    """
    pass

def extract_currency(text: str):
    """
    Examples:                                                                                                                                                                                                  
      - "$50" → "USD"                                                                                                                                                                                            
      - "€45" → "EUR"                                                                                                                                                                                            
      - "50 rupees" → "INR"                                                                                                                                                                                      
      - "100 yen" → "JPY"
    """
    pass

def parse_date(date: str):
    """
    Examples:                                                                                                                                                                                                  
      - "yesterday" → datetime for yesterday                                                                                                                                                                     
      - "last week" → datetime for 7 days ago                                                                                                                                                                    
      - "2024-12-25" → datetime object                                                                                                                                                                           
      - "3 days ago" → datetime for 3 days back
    """
    pass

def extract_merchant(text: str):
    """
    Examples:                                                                                                                                                                                                  
      - "spent $50 at Starbucks" → "Starbucks"                                                                                                                                                                   
      - "bought from Amazon for $100" → "Amazon"                                                                                                                                                                 
      - "dinner at McDonald's" → "McDonald's"
    """
    pass

