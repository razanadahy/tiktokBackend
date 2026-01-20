import secrets
import re

def generate_id():
    while True:
        candidate = secrets.token_urlsafe(16)[:12]
        # Assure 12 chars alphanumériques
        if re.match(r'^[a-zA-Z0-9]{12}$', candidate):
            return candidate