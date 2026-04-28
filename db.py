import os
from pymongo import MongoClient
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Get the MongoDB URI
MONGO_URI = os.getenv("MONGODB_URI")

def get_db_connection(database_name="tamil_font_app"):
    """
    Connects to the MongoDB Cluster and returns the specified database.
    """
    if not MONGO_URI:
        raise ValueError("MONGODB_URI is not set in the environment variables.")
    
    try:
        client = MongoClient(MONGO_URI)
        # Verify the connection
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB Cluster. Database: {database_name}")
        return client[database_name]
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

if __name__ == "__main__":
    db = get_db_connection()
