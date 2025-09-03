# Mock database for user phone number lookups
# In a real application, this would be replaced with actual database queries

USER_PHONE_DATABASE = {
    "abc": "+11111111111",
}

def get_user_phone(user_id: str) -> str | None:
    """
    Lookup phone number for a given user_id
    Returns None if user not found
    """
    return USER_PHONE_DATABASE.get(user_id)

def user_exists(user_id: str) -> bool:
    """
    Check if user exists in the database
    """
    return user_id in USER_PHONE_DATABASE
