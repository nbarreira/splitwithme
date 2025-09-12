from persistence.database import engine
from persistence.models import Friend, FriendExpenseLink, Expense
from sqlmodel import SQLModel, text, Session, select
from faker import Faker
import datetime
import random



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # Foreign keys are disabled in sqlite3 by default
    with Session(engine) as session:
        session.exec(text("PRAGMA foreign_keys = ON"))


def init_db():
    fake = Faker("es_ES")
    expenses = []
    with Session(engine) as session:
        for _ in range(5):
            expenses.append(Expense(description=f"Travel to {fake.city()}", 
                                    date=fake.date_between(datetime.datetime(2024,10,1), datetime.datetime.now()),
                                    amount=float(random.randint(50, 1000))))
            session.add(expenses[-1])
            session.commit()
            session.refresh(expenses[-1])

        for _ in range(10):
            expense_links = []
            used = []
            for _ in range(random.randint(0,4)):
                random_expense = random.randint(0,len(expenses)-1)
                if random_expense in used:
                    continue
                used.append(random_expense)
                expense_link = FriendExpenseLink(expense_id = expenses[random_expense].id,
                                   amount = 0)
                expense_links.append(expense_link)
            friend = Friend(name=fake.first_name(), expense_links=expense_links)
            session.add(friend)
            session.commit()

def init_db_if_empty():
    with Session(engine) as session:
        friends = session.exec(select(Friend))
        if len(friends.all()) == 0:
            init_db()
        else:
            print("DB not empty")


if __name__ == "__main__":
    create_db_and_tables()
    init_db()

