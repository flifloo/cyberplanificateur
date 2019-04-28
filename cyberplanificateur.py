from app import app
from app.models import User, TwitterAPI, TrelloAPI

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "TwitterAPI": TwitterAPI, "TrelloAPI": TrelloAPI}

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
