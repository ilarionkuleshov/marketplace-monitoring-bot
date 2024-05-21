"""Generates api key."""

import secrets
import string

characters = string.ascii_letters + string.digits
api_key = "".join(secrets.choice(characters) for _ in range(40))

print(api_key)
