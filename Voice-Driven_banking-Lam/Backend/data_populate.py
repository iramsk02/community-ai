# backend/data_populate.py

import asyncio
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the refactored Firestore service functions
from services.firestore_db import (
    initialize_firestore,
    get_current_user_id,
    set_user_profile,
    create_or_update_account, # Use the new function for creating accounts
    add_transaction,
    update_account_balance
)

async def populate_random_banking_data(
    username: str,
    account_number: str,
    initial_balance: float,
    account_type: str,
    currency: str,
    num_transactions: int = 5
):
    """
    Uses the firestore_db service to populate Firestore with mock user data.
    """
    logger.info(f"Starting data population for user: '{username}', account: {account_number}")

    # Use the service function to get a consistent user ID based on the username
    user_id = get_current_user_id(username)
    logger.info(f"Using user_id: {user_id}")

    # 1. Ensure Firestore is initialized
    await initialize_firestore()

    # 2. Create/Update User Profile using the service function
    # This data is stored directly on the user's main document
    user_profile_data = {
        "username": username,
        "email": f"{username.lower().replace(' ', '.')}@example.com",
        "created_at": datetime.now()
    }
    await set_user_profile(user_id, user_profile_data)
    logger.info(f"User profile checked/updated for '{username}'.")

    # 3. Create/Update Banking Account using the new service function
    account_data = {
        "balance": initial_balance,
        "type": account_type,
        "currency": currency,
        "username": username,
        "created_at": datetime.now()
    }
    await create_or_update_account(user_id, account_number, account_data)
    logger.info(f"Account '{account_number}' created/updated for '{username}'.")

    # 4. Add Random Transactions
    logger.info(f"Adding {num_transactions} random transactions...")
    current_balance = initial_balance
    for i in range(num_transactions):
        is_debit = random.choice([True, False])
        amount = round(random.uniform(5.0, 300.0), 2)
        
        if is_debit:
            amount = -amount
            description = random.choice(["Coffee Shop", "Online Purchase", "Gas Station", "Groceries"])
        else:
            description = random.choice(["Salary", "Refund", "Freelance Payment"])

        # Create transaction data and add it using the service function
        transaction_data = {
            "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "description": description,
            "amount": amount,
            "type": "debit" if is_debit else "credit",
            "category": random.choice(["Food", "Shopping", "Transport", "Income", "Utilities"]),
            "timestamp": datetime.now()
        }
        await add_transaction(user_id, account_number, transaction_data)
        current_balance += amount
        logger.info(f"  Added transaction: {description}, Amount: {amount:.2f}")

    # 5. Update the final balance on the account document
    await update_account_balance(user_id, account_number, current_balance)
    logger.info(f"Final balance for account '{account_number}' updated to {current_balance:.2f} {currency}.")
    logger.info("-" * 50)


async def main():
    """
    Orchestrates the data population tasks.
    Add or remove calls here to generate the test data you need.
    """
    # --- TASK 1: Populate data for Vickey kumar's Savings account ---
    await populate_random_banking_data(
        username="Vickey kumar",
        account_number="1234567890",
        initial_balance=1500.50,
        account_type="Savings",
        currency="INR",
        num_transactions=7
    )

    # --- TASK 2: Populate data for a new user, Alex Doe ---
    await populate_random_banking_data(
        username="Alex Doe",
        account_number="5555666777",
        initial_balance=2500.00,
        account_type="Savings",
        currency="USD",
        num_transactions=10
    )

    # --- TASK 3: Add a second account for Vickey kumar ---
    await populate_random_banking_data(
        username="Vickey kumar",
        account_number="0987654321",
        initial_balance=8230.75,
        account_type="Current",
        currency="INR",
        num_transactions=15
    )

if __name__ == "__main__":
    # Make sure your .env file is configured before running
    asyncio.run(main())
    logger.info("Script execution completed.")