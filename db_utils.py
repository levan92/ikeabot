import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

DATABASE_URL = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')

class UserLinks(Base):
     __tablename__ = 'user_links'

     id = Column(Integer, primary_key=True)
     chat_id = Column(Integer)
     link = Column(String)

     def __repr__(self):
        return f"<user_links(chat_id={self.chat_id}, link={self.link})>" 

class UserLinksDB:
    def __init__(self,):
        engine = create_engine(DATABASE_URL, echo=True)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def _add(self, chat_id, link):
        user_link = UserLinks(chat_id=chat_id, link=link)
        self.session.add(user_link)

    def replace(self, chat_id, links):
        rows = self.session.query(UserLinks).filter_by(chat_id=chat_id)
        rows.delete(synchronize_session=False)
        for link in links:
            self._add(chat_id, link)
        self.session.commit()

    def get(self, chat_id):
        links = self.session.query(UserLinks).filter_by(chat_id=chat_id).all() 
        return links