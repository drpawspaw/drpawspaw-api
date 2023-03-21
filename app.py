import os
import atexit
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from routes.auth.auth import auth_api
from routes.v1.users.users import user_api
from routes.v1.chatbot.chatbot import chatbot_api
from routes.v1.pets.pets import pet_api
from utils.email_sender.handler import email_scheduler
from apscheduler.schedulers.background import BackgroundScheduler

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
app.register_blueprint(pet_api)

# email scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=email_scheduler, trigger="interval", hours=23) # schedule for every 23 hours to check the emails
scheduler.start()

# shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)