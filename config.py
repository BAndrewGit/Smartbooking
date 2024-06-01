import os
from dotenv import load_dotenv


# Încarcă variabilele de mediu din fișierul Keys.env
load_dotenv(dotenv_path='Keys.env')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
