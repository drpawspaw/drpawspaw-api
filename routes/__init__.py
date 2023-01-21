from flask_pymongo import pymongo

# initialize the database connection
mongo_client = pymongo.MongoClient(
    "mongodb+srv://sample_user:admin123@dev.isia4wb.mongodb.net/?retryWrites=true&w=majority"
)
database_conn = mongo_client['sample_db']