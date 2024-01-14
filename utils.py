import random
import string

# Generate a unique email
def create_user_email(fullname, domain):
    email = f'{fullname.replace(" ", ".").lower()}@{domain}'
    return email

# Generate a random password
def generate_password(string_length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(string_length))
    return password
