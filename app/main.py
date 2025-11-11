from app import create_app
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()

load_dotenv(dotenv_path)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
