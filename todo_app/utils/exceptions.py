class APIError(Exception):
    """Base exception for API-related errors"""
    pass

class AuthenticationError(APIError):
    """Exception raised for authentication errors"""
    pass

class NetworkError(APIError):
    """Exception raised for network-related errors"""
    pass

class ValidationError(APIError):
    """Exception raised for validation errors"""
    pass

class DatabaseError(APIError):
    """Exception raised for database-related errors"""
    pass 