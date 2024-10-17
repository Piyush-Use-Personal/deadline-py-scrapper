
from datetime import datetime

def get_today_date() -> str:
    # Get today's date
    today = datetime.now()
    
    # Format the date as 'DD-Month-YYYY'
    formatted_date = today.strftime("%d-%B-%Y").lower()
    
    return formatted_date