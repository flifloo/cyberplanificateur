from flask import Flask, request, redirect, session, render_template
import twitter_credentials, tweepy

app = Flask(__name__)
app.secret_key = "I'm a very mysterious secret key"

def is_keys(session):
    try:
        session["access_token"]
        session["access_secret_token"]
    except:
        return False
    else:
        return True

def api_login(session):
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key)
    auth.set_access_token(session["access_token"], session["access_secret_token"])
    return tweepy.API(auth)

def api_valid(session):
    try:
        api_login(session).me()
    except:
        return False
    else:
        return True

@app.route("/tlogin")
def t_login():
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key, "https://cyberplanificateur.flifloo.fr/tlogin")
    if request.args.get("oauth_token") and request.args.get("oauth_verifier"):
        auth.request_token = {"oauth_token" : request.args.get("oauth_token"), "oauth_token_secret" : request.args.get("oauth_verifier")}
        try:
            auth.get_access_token(request.args.get("oauth_verifier"))
        except:
            return "Error ! Failed to get access token"
        else:
            session["access_token"] = auth.access_token
            session["access_secret_token"] = auth.access_token_secret
            return "Login !"
    else:
        if is_keys(session) and api_valid(session):
            return "Already login !"
        else:
            return redirect(auth.get_authorization_url())

@app.route("/tlogout")
def t_logout():
    if is_keys(session) and api_valid(session):
        session.pop("access_token", None)
        session.pop("access_secret_token", None)
        return "Logout !"
    else:
        return "Not login !"


@app.route("/tpost")
def t_post():
    if is_keys(session) and api_valid(session):
        api = api_login(session)
        api.update_status("bloup")
        return "Send !"
    else:
        return "Not login !"

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
