from dotenv import load_dotenv
import os

# Load variables from the .env file
load_dotenv()

# Access them
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")
database_url = os.getenv("DATABASE_URL")

# Print them to confirm it's working
print("Username:", username)
print("Password:", password)
print("Database URL:", database_url)

