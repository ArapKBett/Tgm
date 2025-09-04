import asyncio
from telethon import TelegramClient
from config.config import Config
from handlers.message_handler import MessageHandler
from handlers.user_handler import UserHandler
from handlers.activity_handler import ActivityHandler
from monitoring.message_monitor import MessageMonitor
from monitoring.session_monitor import SessionMonitor
from utils.logger import setup_logger
from models.models import init_db

# Initialize logger
logger = setup_logger()

async def main():
    # Initialize database
    init_db()
    
    # Create Telegram client
    client = TelegramClient(
        'monitoring_session',
        Config.API_ID,
        Config.API_HASH
    )
    
    # Start client
    await client.start(phone=Config.PHONE_NUMBER)
    
    logger.info("Client created successfully")
    
    # Initialize all handlers
    message_handler = MessageHandler(client)
    user_handler = UserHandler(client)
    activity_handler = ActivityHandler(client)
    message_monitor = MessageMonitor(client)
    session_monitor = SessionMonitor(client)
    
    # Start monitoring
    message_monitor.start_monitoring()
    session_monitor.start_monitoring()
    
    # Track active sessions periodically
    asyncio.create_task(periodic_session_tracking(user_handler))
    
    logger.info("Monitoring started. Press Ctrl+C to stop.")
    
    # Keep running
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        await client.disconnect()

async def periodic_session_tracking(user_handler):
    while True:
        await user_handler.track_active_sessions()
        await asyncio.sleep(Config.CHECK_INTERVAL)

if __name__ == '__main__':
    asyncio.run(main())
