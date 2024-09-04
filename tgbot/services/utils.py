import random
import re
import string


def generate_confirm_code(length: int = 4) -> str:
    code = ''.join(random.choice(string.digits) for _ in range(length))

    return code


def is_email_valid(email: str) -> bool:
    re_str = r'[^@]+@[^@]+\.[^@]+'

    return bool(re.match(re_str, email))
