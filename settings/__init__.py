import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

APP_SETTINGS = os.getenv('APP_ENV')

if APP_SETTINGS:
    if APP_SETTINGS == 'development':
        from settings.development import *
    elif APP_SETTINGS == 'production':
        from settings.production import *
    elif APP_SETTINGS == 'testing':
        from settings.testing import *
