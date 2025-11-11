from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
print("Using .env file:", dotenv_path)

load_dotenv(dotenv_path)

print("INSTANCE_CONNECTION_NAME =", os.getenv("INSTANCE_CONNECTION_NAME"))
