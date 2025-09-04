import re
from datetime import datetime

def contains_keywords(text, keywords):
    """
    Check if text contains any of the specified keywords
    """
    if not text or not keywords:
        return False
    
    text = text.lower()
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
            return True
    return False

def is_work_hours(work_hours):
    """
    Check if current time is within work hours
    """
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    start_time = work_hours.get('start', '09:00')
    end_time = work_hours.get('end', '18:00')
    
    return start_time <= current_time <= end_time

def format_timestamp(timestamp):
    """
    Format datetime object for display
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text, max_length=100):
    """
    Truncate text to specified length
    """
    if not text:
        return ""
    return text[:max_length] + "..." if len(text) > max_length else text

def get_device_info(session):
    """
    Extract device information from Telethon session
    """
    device_model = getattr(session, 'device_model', 'Unknown')
    system_version = getattr(session, 'system_version', 'Unknown')
    app_version = getattr(session, 'app_version', 'Unknown')
    
    return {
        'device_model': device_model,
        'system_version': system_version,
        'app_version': app_version
    }

def is_weekday():
    """
    Check if today is a weekday
    """
    return datetime.now().weekday() < 5  # 0-4 = Monday-Friday
