from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_data.config import load_config
from .models import Base, User, Ticket

config = load_config('.env')

print('@@@@@@@@@@@@@@@@@@@@@@', config.db.database_url)

engine = create_engine(config.db.database_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_user(tg_id, username):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    if user is None:
        new_user = User(tg_id=tg_id, username=username)
        session.add(new_user)
        session.commit()
        return 1
    else:
        return -1