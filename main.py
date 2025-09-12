from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from persistence.utils import create_db_and_tables, init_db_if_empty

from routers import friends, expenses, friend_expenses

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    init_db_if_empty()
    yield


tags_metadata = [
    {
        "name": "friends",
        "description": "CRUD operations with friends.",
    },
    {
        "name": "expenses",
        "description": "CRUD operations with expenses.",
    },
{
        "name": "friend_expenses",
        "description": "CRUD operations with expenses and friends.",
    }
]

description = """
## 🎯 Intended usage
1. ➕ Create an expense with a description, date and amount
2. 👥 Assign friends to split the expense
3. 💰 Update a friend's credit when you get paid
4. 📊 Check balances: view the credit (what has been paid) and debit (what is still owed) balance for each expense and/or friend


### 👫 Friends
You will able to:
* **➕ Create a friend**: requires only one attribute, the `name` 
* **🔍 Retrieve friend info**: includes the internal `id`, the `name` as well as the total `credit balance` and `debit balance`.
* **📋 Retrive the list of friends**: shows all friends with their `id`, `name`, total `credit balance` and total `debit balance`.
* **📋 Retrive a friend list of expenses**: shows all expenses splitted with the specified friend with their `id`, `description`, `amount`, `num friends` that share the expense, `credit balance` and `debit balance`.
* **✏️ Update a friend**: you can modify the `name` of a friend.
* **❌ Delete a friend**: only possible if their current credit balance is 0.

### 💵 Expenses
You will able to:
* **➕ Create an expense**: requires `description`, `date` (format: YYYY-MM-DD) and `amount`
* **🔍 Retrieve expense info**: includes the internal `id`, the `description`, `date`, `amount` and the total `credit balance`.
* **📋 Retrive the list of expenses**: shows all expenses with their `id`, `description`, `date`, `amount`, `num friends` that split the expense and  total `credit balance`.
* **✏️ Update an expense**: you can change the `description`, `date` or `amount`.
* **❌ Delete an expense**


### 🔗 Friends and expenses
You will able to:

* **👥 Assign a friend to an expense**: their initial credit balance will be 0 by default.
* **🔍 Retrieve friend-expense info**: get the `id`, `name` as well as the`credit balance` and the `debit balance` for a friend relative to a specific expense.
* **📋 Retrieve all friends sharing an expense**:  returns a list with each friend's internal `id`, `name, `credit balance` and `debit balance` for that expense.
* **✏️ Update a friend's credit for an expense**: increases the friend's `credit balance`  by the specified `amount`.  
* **❌ Delete a friend from an expense**: only possible if their current credit balance is 0.

"""

app = FastAPI(
    lifespan=lifespan, 
    title="SplitWithMe",
    summary="Simple API to split expenses with friends",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
)

# Enable CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(friends.router)
app.include_router(expenses.router)
app.include_router(friend_expenses.router)

