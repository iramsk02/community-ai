# backend/services/intent_nlu.py
import json
import logging
import asyncio
from .llm_gemini import get_llm_nlu_response

logger = logging.getLogger(__name__)

# The master prompt is now cleaner and doesn't contain the final user query placeholder.
NLU_PROMPT_TEMPLATE = """
Your task is to act as a Natural Language Understanding (NLU) engine for a voice banking assistant.
Analyze the user's text and return a JSON object with two keys: "intent" and "entities".

Critial points to be mention in list_transactions and check_balance:
1. when asking about credit and debit form by transactions with mentioninig the account type , deafult account type is savings.
2. limit is always a number, if not mentioned then default is 10 and not mention some key word as "last"  than set limit to 5 .
3. when ask about last debit or credit  than you have not set limit because we do not know when debit and credit is done.


1. **"intent"**: Classify the user's text into ONE of the following predefined intents:
    - check_balance
    - list_transactions
    - transfer_money
    - inform_otp
    - get_loan_info
    - help
    - confirm_action
    - cancel_action
    - greeting
    - goodbye
    - unknown (use this if the intent is unclear or not on this list)

2. **"entities"**: Extract any relevant entities. Possible entity types are:
    - account_type (e.g., "savings", "current")
    - limit (a number for transactions)
    - amount (a monetary value)
    - currency (e.g., "rupees", "dollars")
    - recipient (the name of a person or entity)
    - loan_type (e.g., "personal", "home")
    - otp_code (a numeric OTP code)

Return ONLY the JSON object, with no other text or explanations.
For Balances and Transactions, include the account type in entities as saving by default.
---
## EXAMPLES ##
---
Text: "Show me my savings account balance"
JSON:
{
  "intent": "check_balance",
  "entities": {
    "account_type": "savings"
  }
}
---
Text: "What are my last 5 transactions?"
JSON:
{
  "intent": "list_transactions",
  "entities": {
    "limit": 5,
    "account_type": "savings"
  }
}
---
Text: "the code is 123456"
JSON:
 {
   "intent": "inform_otp",
   "entities": {
     "otp_code": "123456"
   }
 }
---
Text: "Can you transfer 500 rupees to Vickey"
JSON:
{
  "intent": "transfer_money",
  "entities": {
    "amount": 500,
    "currency": "rupees",
    "recipient": "Vickey"
  }
}
---
Text: "Tell me about your home loans"
JSON:
{
  "intent": "get_loan_info",
  "entities": {
    "loan_type": "home"
  }
}
---
Text: "hi there"
JSON:
{
  "intent": "greeting",
  "entities": {}
}
---
## END EXAMPLES ##
---
"""

async def get_intent_and_entities(user_query: str ) -> dict | None:
    """
    Uses an LLM to extract intent and entities from a user's query.
    """
    logger.info(f"Performing NLU on query: '{user_query}'")
    
    # Append the final part to the prompt, as per your suggestion.
    final_prompt = f'{NLU_PROMPT_TEMPLATE}\nNow, analyze the following user text.\n\nText: "{user_query}"\nJSON:'
    
    try:
        response_text = await get_llm_nlu_response(final_prompt)
        
        # Handle cases where the response might be None
        if not response_text:
            logger.error("NLU failed. LLM returned an empty response.")
            return {"intent": "unknown", "entities": {}}
            
        parsed_json = json.loads(response_text)
        
        logger.info(f"NLU result: {parsed_json}")
        return parsed_json
        
    except json.JSONDecodeError:
        logger.error(f"NLU failed. LLM returned invalid JSON: {response_text}")
        return {"intent": "unknown", "entities": {}}
    except Exception as e:
        logger.error(f"An error occurred during NLU processing: {e}", exc_info=True)
        return None

# The rest of the file (main function for testing) can remain the same.
# Example usage:
async def main():
    """
    A simple function to test the NLU service with various queries.
    """
    print("--- Testing NLU Service ---")
    
    test_queries = [
        "Hello",
        "Please transfer 500 rupees to Vickey",
        "Show me my last 5 transactions",
        "Hello there!",
        "I want to buy a car" # This should be unknown
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = await get_intent_and_entities(query)
        if result:
            intent = result.get('intent', 'N/A')
            entities = result.get('entities', {})
            print(f"  Intent -> {intent}")
            if entities:
                print(f"  Entities -> {entities}")
        else:
            print("  -> Failed to get NLU result.")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    asyncio.run(main())