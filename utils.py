import hashlib


def password_hash(password: str) -> str:
    m = hashlib.sha512()
    m.update(password.encode('UTF-8'))
    return m.hexdigest()
