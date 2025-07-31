import random
import string


def token_gen():
    # Generate a random four-digit number
    # Generate two random uppercase letters
    letter_part = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
    number_part = random.randint(1000, 9999)

    return f"{number_part}{letter_part}"
