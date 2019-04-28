import tweepy, twitter_credentials

def api_login(session):
    auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key)
    auth.set_access_token(session["access_token"], session["access_secret_token"])
    return tweepy.API(auth)

def is_keys(session):
    try:
        session["access_token"]
        session["access_secret_token"]
    except:
        return False
    else:
        return True

def is_login(session):
    return is_keys(session) and api_login(session).verify_credentials()
