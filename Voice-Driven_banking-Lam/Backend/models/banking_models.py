from pydantic import BaseModel
from typing import Optional, Dict, Any

class BankingQueryRequest(BaseModel):
    """
    Request containing the user's natural language query.
    """
    query_text: str
    user_id: str

class BankingQueryResponse(BaseModel):
    """
    Response containing the natural language answer and any structured data.
    """
    response_text: str
    data: Optional[Dict[str, Any]] = None

class PopulateBankingDataRequest(BaseModel):
    """
    Admin request to populate mock data for a user.
    """
    username: str
    num_transactions: int = 10