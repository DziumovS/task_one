from flask import Flask
from app import bp as api_bp


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)
