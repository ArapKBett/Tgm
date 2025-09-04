from telethon import TelegramClient
from models.models import User, Device, ActivityLog
from models.database import get_db_session
from config.config import Config

class UserHandler:
    def __init__(self, client):
        self.client = client
    
    async def track_active_sessions(self):
        session = get_db_session()
        try:
            # Get all active sessions
            active_sessions = await self.client.get_sessions()
            
            for telethon_session in active_sessions:
                # Extract device information
                device_model = getattr(telethon_session, 'device_model', 'Unknown')
                system_version = getattr(telethon_session, 'system_version', 'Unknown')
                app_version = getattr(telethon_session, 'app_version', 'Unknown')
                
                # Check if this device is already registered
                device = session.query(Device).filter_by(
                    device_model=device_model,
                    system_version=system_version
                ).first()
                
                if not device:
                    # Create a generic user for this device
                    user = User(
                        first_name=f"Device_{device_model}",
                        last_name=system_version
                    )
                    session.add(user)
                    session.flush()  # Get the user ID without committing
                    
                    # Create new device entry
                    device = Device(
                        user_id=user.id,
                        device_model=device_model,
                        system_version=system_version,
                        app_version=app_version
                    )
                    session.add(device)
                    
                    # Log this activity
                    activity = ActivityLog(
                        user_id=user.id,
                        activity_type="new_device",
                        details=f"New device detected: {device_model} ({system_version})"
                    )
                    session.add(activity)
                    
                    # Send alert for new device
                    await self.send_new_device_alert(device_model, system_version)
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error tracking sessions: {e}")
        finally:
            session.close()
    
    async def send_new_device_alert(self, device_model, system_version):
        alert_message = f"📱 New device detected!\n\n"
        alert_message += f"Device: {device_model}\n"
        alert_message += f"OS: {system_version}\n"
        alert_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            await self.client.send_message(Config.ADMIN_CHAT_ID, alert_message)
        except Exception as e:
            print(f"Error sending device alert: {e}")
