import argparse
from models.database import get_db_session
from models.models import MessageLog, User, ActivityLog
from datetime import datetime, timedelta
from tabulate import tabulate

def show_recent_activities(hours=24):
    session = get_db_session()
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    activities = session.query(ActivityLog).filter(
        ActivityLog.timestamp >= time_threshold
    ).all()
    
    table_data = []
    for activity in activities:
        user = session.query(User).filter_by(id=activity.user_id).first()
        table_data.append([
            activity.timestamp.strftime('%Y-%m-%d %H:%M'),
            f"{user.first_name} {user.last_name}",
            activity.activity_type,
            activity.details[:50] + '...' if activity.details and len(activity.details) > 50 else activity.details
        ])
    
    print(tabulate(table_data, headers=['Time', 'User', 'Activity', 'Details']))
    session.close()

def show_non_work_messages(hours=24):
    session = get_db_session()
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    messages = session.query(MessageLog).filter(
        MessageLog.timestamp >= time_threshold,
        MessageLog.is_work_related == False
    ).all()
    
    table_data = []
    for msg in messages:
        user = session.query(User).filter_by(id=msg.user_id).first()
        table_data.append([
            msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            f"{user.first_name} {user.last_name}",
            msg.chat_name,
            msg.message[:50] + '...' if msg.message and len(msg.message) > 50 else msg.message
        ])
    
    print(tabulate(table_data, headers=['Time', 'User', 'Chat', 'Message']))
    session.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram Monitoring Admin Panel')
    parser.add_argument('--activities', type=int, help='Show activities from last N hours')
    parser.add_argument('--non-work', type=int, help='Show non-work messages from last N hours')
    
    args = parser.parse_args()
    
    if args.activities:
        show_recent_activities(args.activities)
    elif args.non_work:
        show_non_work_messages(args.non_work)
    else:
        print("Please specify an option: --activities N or --non-work N")
