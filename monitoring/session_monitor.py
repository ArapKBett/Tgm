from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon.tl.functions.account import GetAuthorizationsRequest
from models.database import get_db_session
from models.models import Device, ActivityLog, User
from config.config import Config
from datetime import datetime, timedelta
import asyncio

class SessionMonitor:
    def __init__(self, client):
        self.client = client
        self.scheduler = AsyncIOScheduler()
    
    def start_monitoring(self):
        # Schedule periodic session checks
        self.scheduler.add_job(
            self.check_sessions, 
            'interval', 
            seconds=Config.CHECK_INTERVAL
        )
        self.scheduler.start()
    
    async def check_sessions(self):
        """
        Check all active sessions and look for anomalies
        """
        session = get_db_session()
        try:
            # Get all authorized sessions from Telegram
            auths = await self.client(GetAuthorizationsRequest())
            
            # Track current sessions
            current_session_ids = []
            for auth in auths.authorizations:
                current_session_ids.append(auth.hash)
                
                # Check if this session is already in our database
                device = session.query(Device).filter_by(
                    device_model=auth.device_model,
                    system_version=auth.system_version
                ).first()
                
                if not device:
                    # New device detected
                    await self.handle_new_device(auth)
                else:
                    # Update last seen time
                    device.last_seen = datetime.utcnow()
                    session.commit()
            
            # Check for sessions that are no longer active
            await self.check_inactive_sessions(current_session_ids)
            
        except Exception as e:
            print(f"Error checking sessions: {e}")
        finally:
            session.close()
    
    async def handle_new_device(self, auth):
        """
        Handle detection of a new device
        """
        session = get_db_session()
        try:
            # Create a generic user for this device
            user = User(
                first_name=f"Device_{auth.device_model}",
                last_name=auth.system_version
            )
            session.add(user)
            session.flush()  # Get the user ID without committing
            
            # Create new device entry
            device = Device(
                user_id=user.id,
                device_model=auth.device_model,
                system_version=auth.system_version,
                app_version=auth.app_version,
                ip_address=auth.ip,
                last_seen=datetime.utcnow()
            )
            session.add(device)
            
            # Log this activity
            activity = ActivityLog(
                user_id=user.id,
                activity_type="new_device",
                details=f"New device detected: {auth.device_model} ({auth.system_version}) at IP: {auth.ip}"
            )
            session.add(activity)
            
            session.commit()
            
            # Send alert for new device
            await self.send_new_device_alert(auth)
            
        except Exception as e:
            session.rollback()
            print(f"Error handling new device: {e}")
        finally:
            session.close()
    
    async def check_inactive_sessions(self, current_session_ids):
        """
        Check for sessions that are no longer active
        """
        session = get_db_session()
        try:
            # Get all devices from database
            all_devices = session.query(Device).all()
            
            for device in all_devices:
                # Check if device hasn't been seen in a while
                time_since_last_seen = datetime.utcnow() - device.last_seen
                if time_since_last_seen > timedelta(hours=24):
                    # Log inactivity
                    activity = ActivityLog(
                        user_id=device.user_id,
                        activity_type="device_inactive",
                        details=f"Device {device.device_model} has been inactive for 24 hours"
                    )
                    session.add(activity)
                    
                    # Optionally send alert
                    if time_since_last_seen > timedelta(days=7):
                        await self.send_inactive_device_alert(device)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Error checking inactive sessions: {e}")
        finally:
            session.close()
    
    async def send_new_device_alert(self, auth):
        """
        Send alert about a new device
        """
        alert_message = f"📱 New device detected!\n\n"
        alert_message += f"Device: {auth.device_model}\n"
        alert_message += f"OS: {auth.system_version}\n"
        alert_message += f"App: {auth.app_version}\n"
        alert_message += f"IP: {auth.ip}\n"
        alert_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, alert_message)
        except Exception as e:
            print(f"Error sending device alert: {e}")
    
    async def send_inactive_device_alert(self, device):
        """
        Send alert about an inactive device
        """
        alert_message = f"📴 Device inactive for over 7 days!\n\n"
        alert_message += f"Device: {device.device_model}\n"
        alert_message += f"OS: {device.system_version}\n"
        alert_message += f"Last seen: {device.last_seen.strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, alert_message)
        except Exception as e:
            print(f"Error sending inactive device alert: {e}")
