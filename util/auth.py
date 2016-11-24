from hashlib import md5

def hmac(data):
    hmac_secret = '$2a$12$4HrCZYbcfR9ebUQ5gWUNb.'
    return md5(data + hmac_secret).hexdigest()

def validate_mac(data, this_mac):
    that_mac = hmac(data)
    return this_mac == that_mac

def validate_user_cookie(cookie):
    user, mac = cookie.split('|')
    return validate_mac(user, mac)

def create_user_cookie(user):
    return "%s|%s" % (user, hmac(user))

if __name__ == "__main__":

    assert validate_user_cookie(create_user_cookie('user')) == True
    assert validate_user_cookie("junk_user|junk_mac") == False