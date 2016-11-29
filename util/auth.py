"""
Comprises a suite of utility functions for carrying out creation and validation
of cookies
"""

from hashlib import md5


def hmac(data):
    """
    Create an message authentication code for a piece of data

    Args:
        data: The data to create and authentication code for

    Returns:
        A message authentication code, as a string
    """
    hmac_secret = '$2a$12$4HrCZYbcfR9ebUQ5gWUNb.'
    return md5(data + hmac_secret).hexdigest()


def validate_mac(data, their_mac):
    """
    Validate a message authentication code

    Args:
        data: The data to salt and hash
        their_mac: The provided MAC to validate

    Returns:
        True if their_mac is valid; False otherwise
    """
    our_mac = hmac(data)
    return our_mac == their_mac


def validate_user_cookie(cookie):
    """
    Validates the MAC of a user's cookie

    Args:
        cookie: A cookie of the form "value|MAC"

    Returns:
        True if hash(value) == MAC; False otherwise
    """

    if cookie:
        user, mac = cookie.split('|')
        return validate_mac(user, mac)

    return False


def create_user_cookie(user):
    """
    Creates a cookie with a message authentication code

    Args:
        user: A username

    Returns:
        A string of the form "username|hash(username)"
    """
    return "%s|%s" % (user, hmac(user))


# If auth.py is running as the main module, check that the cookie validation
# functions are invertible
if __name__ == "__main__":

    assert validate_user_cookie(create_user_cookie('user')) is True
    assert validate_user_cookie("junk_user|junk_mac") is False
