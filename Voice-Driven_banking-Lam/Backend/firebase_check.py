import asyncio
import logging
from dotenv import load_dotenv

# Load .env file for database credentials
load_dotenv()

# Import the service you want to test
from services import firestore_db

# Configure logging to see the output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    A dummy main function to test all data retrieval functions from firestore_db.py.
    """
    logger.info("--- Starting Firestore Functions Test ---")
    
    await firestore_db.initialize_firestore()
    if not firestore_db.db:
        logger.error("Test failed: Could not initialize Firestore.")
        return
    logger.info("Firestore initialized successfully.")

    # --- Hardcode the user and account to test with ---
    test_user_id = "local_user_vickey_kumar"
    test_account_number = "1234567890"

    print("\n" + "="*50)
    # 1. Test get_user_account


    all_accounts = await firestore_db.get_all_user_accounts_summary(test_user_id)
    source_account = next((acc for acc in all_accounts if acc.get("type", "").lower() == "savings"), None)

    print(f"Source Account: {source_account}")
    logger.info(f"1. Testing get_user_account for account: {test_account_number}")
    account_data = await firestore_db.get_user_account(test_user_id, test_account_number)
    if account_data:
        print("   ✅ SUCCESS:", account_data)
    else:
        print(f"   ❌ FAILED to get account {test_account_number}.")

    print("\n" + "="*50)
    # 2. Test get_all_user_accounts
    logger.info(f"2. Testing get_all_user_accounts for user: {test_user_id}")
    all_accounts = await firestore_db.get_all_user_accounts(test_user_id)
    if all_accounts:
        print(f"   ✅ SUCCESS: Found {len(all_accounts)} accounts.")
        print(all_accounts)
    else:
        print("   ❌ FAILED to get all accounts.")

    print("\n" + "="*50)
    # 3. Test get_all_user_accounts_summary
    logger.info(f"3. Testing get_all_user_accounts_summary for user: {test_user_id}")
    summary_accounts = await firestore_db.get_all_user_accounts_summary(test_user_id)
    if summary_accounts:
        print(f"   ✅ SUCCESS: Found {len(summary_accounts)} accounts.")
        print(summary_accounts)
    else:
        print("   ❌ FAILED to get account summaries.")
    
    # target_account_number = None
    # target_account_type = 
    #         if target_account_type:
    #             # If user specified an account type (e.g., "savings")
    #             for acc in all_accounts:
    #                 if acc.get("type", "").lower() == target_account_type:
    #                     target_account_number = acc.get("account_number")
    #                     break


    print("\n" + "="*50)
    # 4. Test get_user_transactions
    logger.info(f"4. Testing get_user_transactions for account: {test_account_number}")
    transactions = await firestore_db.get_user_transactions(test_user_id, test_account_number, limit=3)
    if transactions:
        print(f"   ✅ SUCCESS: Found {len(transactions)} transactions.")
        print(transactions)
    else:
        print("   ❌ FAILED to get transactions.")
    
    print("\n" + "="*50)
    logger.info("--- Test Complete ---")
    
    # getting account detail 
    # account_detail = await firestore_db.get_only_account_no(test_user_id)
    # if account_detail:
    #     print(f"   ✅ SUCCESS: Account detail found: {account_detail}")
    # else:
    #     print("   ❌ FAILED to get account detail.")
    
    # transaction detail
    transaction_detail = await firestore_db.get_user_transactions(test_user_id, test_account_number, limit=5)
    if transaction_detail:
        print(f"   ✅ SUCCESS: Transaction detail found: {transaction_detail}")
    else:
        print("   ❌ FAILED to get transaction detail.")
if __name__ == "__main__":
    asyncio.run(main())