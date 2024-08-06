from argon2 import PasswordHasher

ph = PasswordHasher()


def hash_password(password):
    return ph.hash(password)


def check_password(hashed_password, password):
    try:
        ph.verify(hashed_password, password)
        return True
    except:
        return False
