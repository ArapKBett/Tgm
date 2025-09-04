from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config.config import Config

engine = create_engine(Config.DB_PATH, echo=False)
Session = scoped_session(sessionmaker(bind=engine))

def get_db_session():
    return Session()
