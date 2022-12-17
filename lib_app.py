from flask import Flask
from app import bp as api_bp
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

app = Flask(__name__)
app.config.from_object(f'settings.{os.getenv("APP_ENV")}')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run()
