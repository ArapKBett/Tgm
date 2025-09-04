from telethon import TelegramClient, events
from models.models import ActivityLog, User
from models.database import get_db_session
from config.config import Config
from datetime import datetime

class ActivityHandler:
    def __init__(self, client):
        self.client = client
        self.setup_handlers()
    
    def setup_handlers(self):
        # Track when users come online/offline
        @self.client.on(events.UserUpdate)
        async def handle_user_update(event):
            await self.track_user_activity(event)
        
        # Track when users are typing
        @self.client.on(events.ChatAction)
        async def handle_chat_action(event):
            await self.track_chat_activity(event)
    
    async def track_user_activity(self, event):
        session = get_db_session()
        try:
            user = session.query(User).filter_by(user_id=event.user_id).first()
            if not user:
                # Create new user if not exists
                user_entity = await event.get_user()
                user = User(
                    user_id=event.user_id,
                    first_name=getattr(user_entity, 'first_name', ''),
                    last_name=getattr(user_entity, 'last_name', ''),
                    username=getattr(user_entity, 'username', '')
                )
                session.add(user)
                session.commit()
            
            # Log the activity
            activity_type = "online" if event.online else "offline"
            activity = ActivityLog(
                user_id=user.id,
                activity_type=activity_type,
                details=f"User {activity_type} at {datetime.utcnow()}"
            )
            session.add(activity)
            session.commit()
            
            # Alert if activity is outside work hours
            if not self.is_within_work_hours():
                await self.send_alert(user, f"User activity outside work hours: {activity_type}")
                
        except Exception as e:
            session.rollback()
            print(f"Error tracking user activity: {e}")
        finally:
            session.close()
    
    async def track_chat_activity(self, event):
        session = get_db_session()
        try:
            # Only track typing actions
            if not hasattr(event, 'typing') or not event.typing:
                return
            
            user = session.query(User).filter_by(user_id=event.user_id).first()
            if not user:
                # Create new user if not exists
                user_entity = await event.get_user()
                user = User(
                    user_id=event.user_id,
                    first_name=getattr(user_entity, 'first_name', ''),
                    last_name=getattr(user_entity, 'last_name', ''),
                    username=getattr(user_entity, 'username', '')
                )
                session.add(user)
                session.commit()
            
            # Get chat information
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', getattr(chat, 'username', 'Private Chat'))
            
            # Log the activity
            activity = ActivityLog(
                user_id=user.id,
                activity_type="typing",
                details=f"User typing in {chat_name}"
            )
            session.add(activity)
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Error tracking chat activity: {e}")
        finally:
            session.close()
    
    def is_within_work_hours(self):
        from utils.helpers import is_work_hours
        return is_work_hours(Config.WORK_HOURS)
    
    async def send_alert(self, user, message):
        alert_message = f"🚨 Suspicious activity detected!\n\n"
        alert_message += f"User: {user.first_name} {user.last_name} (@{user.username})\n"
        alert_message += f"Activity: {message}\n"
        alert_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, alert_message)
        except Exception as e:
            print(f"Error sending activity alert: {e}")
