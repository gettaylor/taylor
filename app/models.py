from sqlalchemy import Column, Integer, String
from database import Base

class NewInstall(Base):
    __tablename__ = "new_install"

    id = Column(Integer, primary_key=True)
    bot_access_token = Column(String)
    team_name = Column(String)
    team_id = Column(String)

    def __init__(self, bot_access_token=None, team_name=None, team_id=None):
        self.bot_access_token = bot_access_token
        self.team_name = team_name
        self.team_id = team_id

    def __repr__(self):
        return "<Team(bot_access_token='%s', team_name='%s', team_id='%s')>" % (self.bot_access_token, self.team_name, self.team_id)
        
