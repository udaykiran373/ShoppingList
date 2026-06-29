"""
Custom exception definition for the Shopping List API.
"""

class ShoppingListException(Exception):
    """Custom exception raised for errors in the Shopping List API."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
