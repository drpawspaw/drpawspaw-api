import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from routes.auth.auth import auth_api
from routes.v1.users.users import user_api
from routes.v1.chatbot.chatbot import chatbot_api

# load environment variables
load_dotenv()

# define application configurations
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# handling cross-origin error
CORS(app)

# define module routes
app.register_blueprint(user_api)
app.register_blueprint(auth_api)
app.register_blueprint(chatbot_api)

if __name__ == "__main__":
    app.run(port=8000, debug=True)