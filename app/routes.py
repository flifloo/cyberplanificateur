from app import app, db
from flask import Flask, request, redirect, session, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, TrelloAPIForm
from app.models import User, TwitterAPI, Tweets, TrelloAPI, Boards
from werkzeug.urls import url_parse
import tweepy, trello, twitter_credentials, trello_credentials

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", form = form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/twlogin")
@login_required
def twlogin():
    if current_user.twitter_api.first():
        return "Already an api connected."
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key, "https://cyberplanificateur.flifloo.fr/twlogin")
    if request.args.get("oauth_token") and request.args.get("oauth_verifier"):
        auth.request_token = {"oauth_token" : request.args.get("oauth_token"), "oauth_token_secret" : request.args.get("oauth_verifier")}
        try:
            auth.get_access_token(request.args.get("oauth_verifier"))
        except:
            return "Error ! Failed to get access token"
        else:
            db.session.add(TwitterAPI(access_token = auth.access_token, access_token_secret = auth.access_token_secret, user = current_user))
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
    if current_user.trello_api.first():
        return "Already an api connected."
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
    form = TrelloAPIForm()
    if form.validate_on_submit():
        if current_user.trello_api.first():
            return "Already an api connected."
        db.session.add(TrelloAPI(token = form.token.data, user = current_user))
        db.session.commit()
    return render_template("settings.html", form = form)

@app.route("/dashboard", methods = ["POST", "GET"])
@login_required
def dashboard():
    twapi = current_user.twitter_api.first()
    trapi = current_user.trello_api.first()
    tweets = list()
    timeline = list()
    boards = list()
    columns = list()

    if twapi:
        twapi = twapi.api_login()

        if request.args.get("twrm"):
            t = Tweets.query.filter_by(user = current_user, statu_id = request.args.get("twrm")).first()
            for c in t.commissions.all():
                db.session.delete(c)
            db.session.delete(t)
            db.session.commit()
            if request.args.get("delet"):
                twapi.destroy_status(request.args.get["twrm"])
        elif "tweet" in request.form and "slots" in request.form and "keywords" in request.form:
            try:
                slots = int(request.form["slots"])
                tweet = int(request.form["tweet"])
            except:
                formerror = True
            else:
                db.session.add(Tweets(user = current_user, statu_id = tweet, slots = 0, slots_max = slots, keywords = str(request.form["keywords"].split(","))))
                db.session.commit()
        elif "board" in request.form:
            db.session.add(Boards(user = current_user, board_id = request.form["board"]))
            db.session.commit()
        elif "column" in request.form:
            current_user.boards.first().column_id = request.form["column"]
            db.session.commit()

        for t in Tweets.query.filter_by(user = current_user):
            statu = twapi.get_status(t.statu_id)
            keywords = "|"
            for text in eval(t.keywords):
                keywords += f" {text} |"
            tweets.append({"text": statu.text, "id": t.statu_id, "slots": f"{t.slots}/{t.slots_max}", "keywords": keywords})

        for t in twapi.user_timeline(count = 200):
            if not t.in_reply_to_status_id and not t.retweeted and not Tweets.query.filter_by(user = current_user, statu_id = t.id).first():
                if len(timeline) >= 5:
                    break
                timeline.append({"text": t.text, "id": t.id})


    if trapi:
        trapi = trapi.api_login()
        for b in trapi.list_boards():
            select = False
            if current_user.boards.first() and b.id == current_user.boards.first().board_id:
                select = True
            boards.append({"text": b.name, "id": b.id, "select": select})

        if current_user.boards.first() and current_user.boards.first().board_id:
            for c in trapi.get_board(current_user.boards.first().board_id).list_lists():
                select = False
                if c.id == current_user.boards.first().column_id:
                    select = True
                columns.append({"text": c.name, "id": c.id, "select": select})

    return render_template("dashboard.html", timeline = timeline, tweets = tweets, boards = boards, columns = columns)

@app.route("/test")
def test():
    return render_template("elements.html")
