import random
import string
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_name(name):
    normalized = remove_accents(name)
    return normalized.strip().lower()

# Generate a unique email
def create_user_email(fullname, domain):
    email = f'{normalize_name(fullname).replace(" ", ".")}@{domain}'
    return email

# Generate a random password
def generate_password(string_length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(string_length))
    return password

# Gets a list of errors from an exception and its causes
def get_error_chain(exception):
    errors = []
    while exception is not None:
        errors.append({
            'type': type(exception).__name__,
            'message': str(exception),
        })
        exception = exception.__cause__
    return errors