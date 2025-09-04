from telethon import TelegramClient, events
from models.models import MessageLog, User
from models.database import get_db_session
from config.config import Config
from utils.helpers import contains_keywords, is_work_hours
import re

class MessageHandler:
    def __init__(self, client):
        self.client = client
        self.keywords = Config.KEYWORD_ALERTS
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            await self.process_message(event)
    
    async def process_message(self, event):
        session = get_db_session()
        try:
            # Get user information
            user = session.query(User).filter_by(user_id=event.sender_id).first()
            if not user:
                # Create new user if not exists
                user_entity = await event.get_sender()
                user = User(
                    user_id=event.sender_id,
                    first_name=getattr(user_entity, 'first_name', ''),
                    last_name=getattr(user_entity, 'last_name', ''),
                    username=getattr(user_entity, 'username', '')
                )
                session.add(user)
                session.commit()
            
            # Get chat information
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', getattr(chat, 'username', 'Private Chat'))
            
            # Analyze message
            message_text = event.raw_text
            is_work_related = self.analyze_message(message_text)
            
            # Log message
            message_log = MessageLog(
                user_id=user.id,
                chat_id=event.chat_id,
                chat_name=chat_name,
                message=message_text,
                message_type=self.get_message_type(event),
                is_work_related=is_work_related,
                flagged=not is_work_related
            )
            session.add(message_log)
            session.commit()
            
            # Send alert if needed
            if not is_work_related:
                await self.send_alert(user, message_text, chat_name)
                
        except Exception as e:
            session.rollback()
            print(f"Error processing message: {e}")
        finally:
            session.close()
    
    def analyze_message(self, message):
        # Check if message contains non-work related keywords
        if contains_keywords(message, self.keywords):
            return False
        
        # Check if it's during work hours
        if not is_work_hours(Config.WORK_HOURS):
            return False
            
        return True
    
    def get_message_type(self, event):
        if event.photo:
            return "photo"
        elif event.video:
            return "video"
        elif event.document:
            return "document"
        elif event.voice:
            return "voice"
        else:
            return "text"
    
    async def send_alert(self, user, message, chat_name):
        alert_message = f"🚨 Non-work related activity detected!\n\n"
        alert_message += f"User: {user.first_name} {user.last_name} (@{user.username})\n"
        alert_message += f"Chat: {chat_name}\n"
        alert_message += f"Message: {message[:200]}...\n"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, alert_message)
        except Exception as e:
            print(f"Error sending alert: {e}")
