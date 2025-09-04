import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API credentials
    API_ID = int(os.getenv('API_ID', 0))
    API_HASH = os.getenv('API_HASH', '')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')
    
    # Database
    DB_PATH = os.getenv('DB_PATH', 'sqlite:///monitoring.db')
    
    # Monitoring settings
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutes
    KEYWORD_ALERTS = eval(os.getenv('KEYWORD_ALERTS', "['game', 'movie', 'entertainment', 'personal']"))
    WORK_HOURS = eval(os.getenv('WORK_HOURS', "{'start': '09:00', 'end': '18:00'}"))
    
    # Admin settings
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))
    ALERT_LEVEL = os.getenv('ALERT_LEVEL', 'high')  # high, medium, low
