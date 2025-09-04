import logging
from datetime import datetime
import os

def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f"logs/monitoring_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('TelegramMonitor')
