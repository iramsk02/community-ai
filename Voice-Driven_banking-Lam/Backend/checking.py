import asyncio
import logging
import uuid
from dotenv import load_dotenv

# Load .env file for database credentials
load_dotenv()

# Import the services we need to test
from services import firestore_db
from services import firestore_session

# Configure logging to see the output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    A dummy main function to test session creation and history updates with turn_ids.
    """
    logger.info("--- Starting Firestore Session Test with Turn IDs ---")
    
    await firestore_db.initialize_firestore()
    if not firestore_db.db:
        logger.error("Test failed: Could not initialize Firestore.")
        return
    logger.info("Firestore initialized successfully.")

    # 1. Define dummy data
    test_session_id = f"dummy_session_{uuid.uuid4()}"
    test_user_id = "local_test_user_123"
    
    # --- First conversation turn ---
    logger.info(f"Appending first turn to session: {test_session_id}")
    await firestore_session.append_to_session(
        session_id=test_session_id,
        user_id=test_user_id,
        user_query="Hello, what is my balance?",
        assistant_response="Your balance is one thousand rupees."
    )

    # --- Second conversation turn ---
    logger.info(f"Appending second turn to session: {test_session_id}")
    await firestore_session.append_to_session(
        session_id=test_session_id,
        user_id=test_user_id,
        user_query="Thank you",
        assistant_response="You're welcome!"
    )

    # 2. Read the full history back to verify
    logger.info(f"Reading full history from session: {test_session_id}")
    final_history = await firestore_session.get_sessionid_history(
        session_id=test_session_id,
        user_id=test_user_id
    )

    # 3. Check the result and verify the turn_ids
    if final_history and len(final_history) == 4:
        turn_1_id = final_history[0].get("turn_id")
        turn_2_id = final_history[2].get("turn_id")

        # Check if IDs exist and are consistent within a turn, but different between turns
        if (turn_1_id and turn_2_id and
            final_history[0]["turn_id"] == final_history[1]["turn_id"] and
            final_history[2]["turn_id"] == final_history[3]["turn_id"] and
            turn_1_id != turn_2_id):
            
            logger.info("✅ TEST PASSED: Successfully wrote and retrieved the history with correct turn_ids.")
            print("\n--- Retrieved History ---")
            for message in final_history:
                print(f"- Turn ID: {message.get('turn_id')}, Role: {message.get('role')}, Content: {message.get('content')}")
            print("------------------------")
        else:
            logger.error("❌ TEST FAILED: The turn_ids are incorrect or missing.")
            print(f"\nRetrieved History: {final_history}")
    else:
        logger.error("❌ TEST FAILED: The retrieved history was incorrect or empty.")
        print(f"\nRetrieved History: {final_history}")

    logger.info("--- Test Complete ---")


if __name__ == "__main__":
    asyncio.run(main())