import os
import random
import string


def random_bytes(count: int):
    return os.urandom(count)


def random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def generate_one_time_id():
    return random_string(12)
