from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models.database import get_db_session
from models.models import MessageLog
from config.config import Config
from datetime import datetime, timedelta
import asyncio

class MessageMonitor:
    def __init__(self, client):
        self.client = client
        self.scheduler = AsyncIOScheduler()
    
    def start_monitoring(self):
        # Schedule periodic checks
        self.scheduler.add_job(
            self.check_recent_activities, 
            'interval', 
            seconds=Config.CHECK_INTERVAL
        )
        self.scheduler.start()
    
    async def check_recent_activities(self):
        session = get_db_session()
        try:
            # Check messages from the last CHECK_INTERVAL
            time_threshold = datetime.utcnow() - timedelta(seconds=Config.CHECK_INTERVAL)
            
            # Get non-work related messages
            non_work_messages = session.query(MessageLog).filter(
                MessageLog.timestamp >= time_threshold,
                MessageLog.is_work_related == False
            ).all()
            
            if non_work_messages:
                await self.send_periodic_report(non_work_messages)
                
        except Exception as e:
            print(f"Error in periodic check: {e}")
        finally:
            session.close()
    
    async def send_periodic_report(self, messages):
        report_message = "📊 Periodic Activity Report\n\n"
        report_message += f"Time period: Last {Config.CHECK_INTERVAL} seconds\n"
        report_message += f"Non-work activities detected: {len(messages)}\n\n"
        
        # Group by user
        user_activities = {}
        for msg in messages:
            user_id = msg.user_id
            if user_id not in user_activities:
                user_activities[user_id] = []
            user_activities[user_id].append(msg)
        
        for user_id, msgs in user_activities.items():
            user = session.query(User).filter_by(id=user_id).first()
            report_message += f"User: {user.first_name} {user.last_name} - {len(msgs)} activities\n"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, report_message)
        except Exception as e:
            print(f"Error sending periodic report: {e}")
