
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel

class Message(BaseModel):
    detail: str


class FriendExpenseLink(SQLModel, table=True):
    friend_id: Optional[int] = Field(default=None, foreign_key="friend.id", primary_key=True)    
    expense_id: Optional[int] = Field(default=None, foreign_key="expense.id", primary_key=True)
    amount: float = Field(default = 0)

    friend: "Friend" = Relationship(back_populates="expense_links")
    expense: "Expense" = Relationship(back_populates="friend_links")


class Friend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  
    expense_links: list["FriendExpenseLink"] = Relationship(back_populates="friend", cascade_delete=True)
    credit_balance: float = Field(default = 0)
    debit_balance: float = Field(default = 0)


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    date: str
    amount: float
    credit_balance: Optional[float] = Field(default = 0)
    num_friends: Optional[int] = Field(default = 1)
    friend_links: list["FriendExpenseLink"] = Relationship(back_populates="expense", cascade_delete=True)

class FriendExpense(BaseModel):
    id: int
    description: str
    amount: float
    num_friends: int
    credit_balance: float
    debit_balance: float