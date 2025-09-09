from fastapi import APIRouter, Depends, HTTPException
from persistence.database import get_session
from persistence.models import Message, Friend, Expense, FriendExpenseLink, Expense
from sqlmodel import Session, select, func


router = APIRouter(
    prefix = "/expenses",
    tags=["friend_expenses"]
)


@router.post("/{expense_id}/friends",
          status_code=201,
          responses={201: {"model": Expense},
                     404: {"model": Message}, 
                     409: {"model": Message}})
def add_friend_to_expense(expense_id: int, friend_id: int, session: Session = Depends(get_session)) -> FriendExpenseLink:
    existing_friend = session.exec(select(Friend).where(Friend.id==friend_id)).first()
    if existing_friend is None:
        raise  HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")
    existing_expense = session.exec(select(Expense).where(Expense.id==expense_id)).first()
    if existing_expense is None:
         raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")
    existing_friend_expense = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id).where(FriendExpenseLink.friend_id == friend_id))
    if existing_friend_expense.first() is None:
        friend_expense_link = FriendExpenseLink(expense_id=expense_id, friend_id=friend_id)
        session.add(friend_expense_link)
        session.commit()
        session.refresh(friend_expense_link)
        return friend_expense_link
    else:
        raise HTTPException(status_code=409, detail="Friend was previously assigned to expense")



@router.get("/{expense_id}/friends",
         responses={200: {"model": list[Friend]}, 404: {"model": Message}})
def get_friends_by_expense(expense_id: int, session: Session = Depends(get_session)) -> list[Friend]:
    expense = session.exec(select(Expense).where(Expense.id == expense_id)).first()
    if expense is not None:
        friends_by_expense = expense.friend_links
        friends = []
        debit_per_friend = expense.amount / (len(friends_by_expense)+1)

        for friend_by_expense in friends_by_expense:
            friend = friend_by_expense.friend
            friend.credit_balance = friend_by_expense.amount
            friend.debit_balance = debit_per_friend
            friends.append(friend)
    
        return friends
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")


@router.get("/{expense_id}/friends/{friend_id}", summary="Get Friend info by Expense",
         responses={200: {"model": Friend}, 404: {"model": Message}})
def get_expenses(expense_id: int, friend_id: int, session: Session = Depends(get_session)) -> Friend:
    friend_by_expense = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id).where(FriendExpenseLink.friend_id == friend_id)).first()
    if friend_by_expense is not None:
        expense = friend_by_expense.expense
        debit_per_friend = expense.amount / (len(expense.friend_links)+1)
        friend = friend_by_expense.friend
        friend.credit_balance = friend_by_expense.amount
        friend.debit_balance = debit_per_friend
        
        return friend
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' for friend '{friend_id}' not found")
    
@router.put("/{expense_id}/friends/{friend_id}", summary="Update Friend's credit in Expense",
         status_code=204,
         responses={404: {"model": Message}})
def update_expense(expense_id: int, friend_id: int, amount: float, session: Session = Depends(get_session)):
    friend_by_expense = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id).where(FriendExpenseLink.friend_id == friend_id)).first()

    if friend_by_expense is not None:
        friend_by_expense.amount += amount
        session.commit()
        session.refresh(friend_by_expense)
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' for friend '{friend_id}' not found")
    
@router.delete("/{expense_id}/friends/{friend_id}", summary="Delete Friend from Expense",
         status_code=204,
         responses={404: {"model": Message},
                    409: {"model": Message}})
def delete_expense(expense_id: int, friend_id: int, session: Session = Depends(get_session)):
    friend_by_expense = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id).where(FriendExpenseLink.friend_id == friend_id)).first()
    if friend_by_expense is not None:
        if friend_by_expense.amount == 0:
            session.delete(friend_by_expense)
            session.commit()  
        else:
            raise HTTPException(status_code=409, detail=f"Credit balance of friend '{friend_id}' in expense '{expense_id}' is not zero")
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' for friend '{friend_id}' not found")