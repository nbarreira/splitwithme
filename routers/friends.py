from fastapi import APIRouter, Depends, HTTPException
from persistence.database import get_session
from persistence.models import Message, Friend, FriendExpenseLink, FriendExpense
from sqlmodel import Session, select, func


router = APIRouter(
    prefix = "/friends",
    tags=["friends"]
)


@router.post("/",
          status_code=201,
          responses={201: {"model": Friend}, 409: {"model": Message}})
def add_friend(friend: Friend, session: Session = Depends(get_session)) -> Friend:
    existing_friend = session.exec(select(Friend).where(Friend.id == friend.id))
    if existing_friend.first() is None:
        session.add(friend)
        session.commit()
        session.refresh(friend)
        return friend
    else:
        raise HTTPException(status_code=409, detail="Friend already exists")


def get_credit_balance(friend_id: int, session: Session) -> float:
    # Sum all the contributions of the friend
    credit_balance = session.exec(select(func.sum(FriendExpenseLink.amount)).where(FriendExpenseLink.friend_id == friend_id)).first()
    if credit_balance is None:
        credit_balance = 0
    return credit_balance

def get_debit_balance(friend_id: int, session: Session) -> float:
    # Get all the expenses this friend has 
    expense_links = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.friend_id == friend_id)).all()
    debit_balance = 0
    for expense_link in expense_links:
        # Get the amount of each expense
        total_amount = expense_link.expense.amount
        # and the number of friends involved plus the user himself/herself
        num_friends = len(expense_link.expense.friend_links) + 1
        debit_balance += total_amount / num_friends
    return debit_balance

@router.get("/{friend_id}",
         responses={200: {"model": Friend}, 404: {"model": Message}})
def get_friend(friend_id: int, session: Session = Depends(get_session)) -> Friend:
    results = session.exec(select(Friend).where(Friend.id == friend_id))
    friend = results.first()
    if friend is not None:
        friend.credit_balance = get_credit_balance(friend_id, session)
        friend.debit_balance = get_debit_balance(friend_id, session)
        return friend
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")


@router.get("/{friend_id}/expenses", summary="Get Expenses by Friend",
         responses={200: {"model": FriendExpense}, 404: {"model": Message}})
def get_friend(friend_id: int, session: Session = Depends(get_session)) -> list[FriendExpense]:
    friend = session.exec(select(Friend).where(Friend.id == friend_id)).first()
    if friend is not None:
        friend_expenses = []
        for friend_expense_link in friend.expense_links:
            expense = friend_expense_link.expense
            num_friends = len(expense.friend_links)
            friend_expenses.append(FriendExpense(id=expense.id, 
                                                 description=expense.description,
                                                 amount=expense.amount,
                                                 num_friends=num_friends + 1,
                                                 credit_balance=friend_expense_link.amount,
                                                 debit_balance=expense.amount/(num_friends+1)))
        
        return friend_expenses
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")


@router.get("/",
         responses={200: {"model": list[Friend]}, 404: {"model": Message}})
def get_friends(session: Session = Depends(get_session)) -> list:
    friends = session.exec(select(Friend)).all()
    for friend in friends:
        friend.credit_balance = get_credit_balance(friend.id, session)
        friend.debit_balance = get_debit_balance(friend.id, session)
    return friends

@router.put("/{friend_id}",
         status_code=204,
         responses={404: {"model": Message}})
def update_friend(friend_id: int, friend: Friend, session: Session = Depends(get_session)):
    results = session.exec(select(Friend).where(Friend.id == friend_id))
    stored_friend = results.first()
    if stored_friend is not None:
        stored_friend.name = friend.name
        session.commit()
        session.refresh(stored_friend)
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")
    
@router.delete("/{friend_id}",
         status_code=204,
         responses={404: {"model": Message},
                    409: {"model": Message}})
def delete_friend(friend_id: int, session: Session = Depends(get_session)):
    results = session.exec(select(Friend).where(Friend.id == friend_id))
    stored_friend = results.first()
    if stored_friend is not None:
        credit_balance = get_credit_balance(friend_id, session)
        if credit_balance == 0:
            session.delete(stored_friend)
            session.commit()
        else:
            raise HTTPException(status_code=409, detail=f"Credit balance of '{friend_id}' is not zero")
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")