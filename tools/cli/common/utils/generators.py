import secrets
import string


def random_string_generator(length: int = 8) -> str:
    """
    Generates a random alphanumeric string
    :param length: length of the string
    :return: alphanumeric string
    """
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(length))
