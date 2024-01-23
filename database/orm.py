from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_data.config import load_config
from .models import Base, User, Ticket

config = load_config('.env')

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
    
def get_user(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    return user
    
def add_ticket(tg_id, date, direction):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    ticket = session.query(Ticket).filter_by(user_id=user.id, date=date, direction=direction).first()
    if ticket is None:
        new_ticket = Ticket(user_id=user.id, date=date, direction=direction)
        session.add(new_ticket)
        session.commit()
        return True
    else:
        return False


def get_tickets(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    tickets = session.query(Ticket).filter_by(user_id=user.id).all()
    return tickets


def delete_ticket(ticket_id):
    session = Session()
    ticket = session.get(Ticket, ticket_id)
    session.delete(ticket)
    session.commit()


def get_ticket_by_id(ticket_id):
    session = Session()
    ticket = session.get(Ticket, ticket_id)
    return ticket

def get_date_and_direction_from_ticket_id(ticket_id):
    session = Session()
    ticket = session.get(Ticket, ticket_id)
    date = ticket.date
    direction = ticket.direction
    return date, direction

def get_all_users():
    session = Session()
    users = session.query(User).all()
    return users


def get_all_ticket_ids():
    session = Session()
    tickets = session.query(Ticket).all()
    ticket_ids = [int(ticket.id) for ticket in tickets]
    return ticket_ids

def get_user_settings(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    everyday_message = user.everyday_message
    return everyday_message

def disable_everyday_message(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    user.everyday_message = False
    session.add(user)
    session.commit()

def enable_everyday_message(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    user.everyday_message = True
    session.add(user)
    session.commit()

def is_premium_user(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    return user.premium

def disable_premium(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    user.premium = False
    session.add(user)
    session.commit()

def enable_premium(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    user.premium = True
    session.add(user)
    session.commit()
