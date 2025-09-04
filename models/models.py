from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    phone = Column(String(20))
    is_authorized = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    device_model = Column(String(100))
    system_version = Column(String(50))
    app_version = Column(String(50))
    ip_address = Column(String(45))
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageLog(Base):
    __tablename__ = 'message_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer)
    chat_name = Column(String(200))
    message = Column(Text)
    message_type = Column(String(50))  # text, photo, video, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_work_related = Column(Boolean, default=True)
    flagged = Column(Boolean, default=False)

class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_type = Column(String(50))  # login, logout, message_sent, etc.
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))

# Create tables
def init_db():
    from models.database import engine
    Base.metadata.create_all(engine)
