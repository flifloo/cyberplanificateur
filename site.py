from flask import Flask, request, redirect, session, render_template
import twitter_credentials, tweepy, database, trello_credentials, trello

app = Flask(__name__)
app.secret_key = "*i9uld6u@t!kxl9%o+byxqf14&a&&@y@q=l$!lg4m%b-a*^o(a"

def is_twkeys(session):
    try:
        session["access_token"]
        session["access_secret_token"]
    except:
        return False
    else:
        return True

def twapi_login(session):
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key)
    auth.set_access_token(session["access_token"], session["access_secret_token"])
    return tweepy.API(auth)

def is_twlogin(session):
    return is_twkeys(session) and twapi_login(session).verify_credentials()

def is_trlogin(session):
    return is_twkeys(session) and database.trtoken(twapi_login(session).me().id)

@app.route("/twlogin")
def twlogin():
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key, "https://cyberplanificateur.flifloo.fr/twlogin")
    if request.args.get("oauth_token") and request.args.get("oauth_verifier"):
        auth.request_token = {"oauth_token" : request.args.get("oauth_token"), "oauth_token_secret" : request.args.get("oauth_verifier")}
        try:
            auth.get_access_token(request.args.get("oauth_verifier"))
        except:
            return "Error ! Failed to get access token"
        else:
            session["access_token"] = auth.access_token
            session["access_secret_token"] = auth.access_token_secret
    elif not is_twlogin(session):
        return redirect(auth.get_authorization_url())
    return redirect("/")

@app.route("/twlogout")
def twlogout():
    if is_twkeys(session):
        session.pop("access_token", None)
        session.pop("access_secret_token", None)
    return redirect("/")


@app.route("/trlogout")
def trlogout():
    if not is_twlogin(session):
        return redirect("/")
    if is_trlogin(session):
        database.trrm(twapi_login(session).me().id)
    return redirect("/settings")

@app.route("/")
def home():
    return render_template("index.html", login = is_twlogin(session))

@app.route("/settings", methods = ['POST', 'GET'])
def settings():
    if not is_twlogin(session):
        return redirect("/")

    trloginfail = False
    if "trtoken" in request.form:
        try:
            trello.TrelloClient(api_key = trello_credentials.api_key, token = request.form["trtoken"]).list_boards()
        except:
            trloginfail = True
        else:
            database.tradd(twapi_login(session).me().id, request.form["trtoken"])
    return render_template("settings.html", login = True, trlogin = is_trlogin(session), trloginfail = trloginfail)

@app.route("/dashboard")
def dashboard():
    if not is_twlogin(session):
        return redirect("/")

    return render_template("dashboard.html", login = True, tweets = ["test1", "test2", "test3"], timeline = [{"id": 1, "text": "test1"}, {"id": 2, "text": "test2"}, {"id": 3, "text": "test3"}, {"id": 4, "text": "test4"}])

@app.route("/twpost")
def twpost():
    if is_twlogin(session):
        api = twapi_login(session)
        api.update_status("bloup")
        return "Send !"
    else:
        return "Not login !"

@app.route("/test")
def test():
    return render_template("elements.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
