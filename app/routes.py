from app import app, db
from flask import Flask, request, redirect, session, render_template, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm
from app.models import User, TwitterAPI, TrelloAPI
from werkzeug.urls import url_parse
import twitter_credentials, tweepy, tw
import trello_credentials, trello, tr

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/twlogin")
@login_required
def twlogin():
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key, "https://cyberplanificateur.flifloo.fr/twlogin")
    if request.args.get("oauth_token") and request.args.get("oauth_verifier"):
        auth.request_token = {"oauth_token" : request.args.get("oauth_token"), "oauth_token_secret" : request.args.get("oauth_verifier")}
        try:
            auth.get_access_token(request.args.get("oauth_verifier"))
        except:
            return "Error ! Failed to get access token"
        else:
            twapi = TwitterAPI(access_token = auth.access_token, access_token_secret = auth.access_token_secret, user = current_user)
            db.session.add(twapi)
            db.session.commit()
    elif not TwitterAPI.query.filter_by(user=current_user).first():
        return redirect(auth.get_authorization_url())
    return redirect(url_for("settings"))

@app.route("/twlogout")
@login_required
def twlogout():
    twapi = TwitterAPI.query.filter_by(user=current_user).first()
    if twapi:
        db.session.delete(twapi)
        db.session.commit()
    return redirect(url_for("settings"))

@app.route("/trlogin")
@login_required
def trlogin():
    return redirect(f"https://trello.com/1/authorize?expiration=never&name=Cyberplanificateur&scope=read,write&response_type=token&key={trello_credentials.api_key}&return_url=https://cyberplanificateur.flifloo.fr/settings")

@app.route("/trlogout")
@login_required
def trlogout():
    trapi = TrelloAPI.query.filter_by(user=current_user).first()
    if trapi:
        db.session.delete(trapi)
        db.session.commit()
    return redirect(url_for("settings"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/settings", methods = ["POST", "GET"])
@login_required
def settings():
    trloginfail = False
    if "trtoken" in request.form:
        try:
            trello.TrelloClient(api_key = trello_credentials.api_key, token = request.form["trtoken"]).list_boards()
        except:
            trloginfail = True
        else:
            trapi = TrelloAPI(token = request.form["trtoken"], user = current_user)
            db.session.add(trapi)
            db.session.commit()
    return render_template("settings.html", twlogin = TwitterAPI.query.filter_by(user=current_user).first(), trlogin = TrelloAPI.query.filter_by(user=current_user).first(), trloginfail = trloginfail)

@app.route("/dashboard", methods = ["POST", "GET"])
def dashboard():
    if not tw.is_login(session):
        return redirect("/")

    twapi = tw.api_login(session)
    if request.args.get("twrm"):
        database.twrm(request.args.get("twrm"))
        if request.args.get("delet"):
            twapi.destroy_status(request.args.get["twrm"])
    elif "tweet" in request.form and "slots" in request.form and "keywords" in request.form:
        try:
            slots = int(request.form["slots"])
            tweet = int(request.form["tweet"])
        except:
            formerror = True
        else:
            database.twadd(twapi.me().id, tweet, slots, str(request.form["keywords"].split(",")))
            formerror = False

    tweets = list()
    idtake = list()
    for t in database.twlist(twapi.me().id):
        tw = twapi.get_status(t["id"])
        keywords = "|"
        for te in eval(t["keywords"]):
            keywords += f" {te} |"
        tweets.append({"text": tw.text, "id": tw.id, "slots": f"{t['slots']}/{t['maxslots']}", "keywords": keywords})
        idtake.append(tw.id)

    timeline = list()
    for t in twapi.user_timeline():
        if not t.in_reply_to_status_id and not t.retweeted and t.id not in idtake:
            timeline.append({"text": t.text, "id": t.id})

    if tr.is_login(session):
        trapi = trello.TrelloClient(api_key = trello_credentials.api_key, token = database.trtoken(twapi.me().id))
        boards = list()
        for b in trapi.list_boards():
            boards.append(b.name)


    return render_template("dashboard.html", login = True, tweets = tweets, timeline = timeline, boards = boards, columns = None)

@app.route("/twtoken")
def twtoken():
    return f"{session['access_token']} -- {session['access_secret_token']}"

@app.route("/twpost")
def twpost():
    if tw.is_login(session):
        api = twapi_login(session)
        api.update_status("bloup")
        return "Send !"
    else:
        return "Not login !"

@app.route("/test")
def test():
    return render_template("elements.html")
