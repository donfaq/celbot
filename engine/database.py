from celery.utils.log import get_task_logger

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    dt = Column(DateTime)
    source = Column(String)
    author = Column(String)
    text = Column(String)

    def __repr__(self):
        return "<Message('%d', %s, '%s', %s, '%s')>" % (self.id, self.dt, self.source, self.author, self.text)


class DatabaseWrapper:
    def __init__(self, database_url):
        self.logger = get_task_logger(self.__class__.__name__)
        self.logger.info("Connecting to database")
        self.engine = create_engine(database_url, echo=True)
        self.logger.info("Successfully connected to DB. Creating structure")
        Base.metadata.create_all(self.engine)
        self.logger.info("All tables ready")
        self.Session = sessionmaker(bind=self.engine)

    def save_new_message(self, dt, source: str, author: str, text: str):
        session = self.Session()
        message = Message(dt=dt, source=source, author=author, text=text)
        session.add(message)
        session.commit()
        session.close()

    def select_all_texts(self):
        session = self.Session()
        result = session.query(Message.text).all()
        session.close()
        return result
