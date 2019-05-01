import tweepy, twitter_credentials, trello, trello_credentials, json, subprocess, argparse
from app import db
from app.models import User, Commission

parser = argparse.ArgumentParser()
parser.add_argument("user", type = int, help = "User id")
args = parser.parse_args()
user = User.query.filter_by(id = args.user).first()

auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key)
auth.set_access_token(user.twitter_api.first().access_token, user.twitter_api.first().access_token_secret)
api = tweepy.API(auth)

class listener(tweepy.streaming.StreamListener):
    def on_data(self, data):
        print(data)
        all_data = json.loads(data)
        for t in user.tweets.all():
            if "in_reply_to_status_id" in all_data and all_data["in_reply_to_status_id"] and t.statu_id == int(all_data["in_reply_to_status_id"]) and t.slots != t.slots_max and not t.commissions.filter_by(user = all_data["user"]["screen_name"]).first() and api.me().id != int(all_data["user"]["id"]):
                for w in eval(t.keywords.lower()):
                    if all_data["text"].lower().find(w) != -1:
                        t.slots += 1
                        db.session.add(Commission(tweet = t, user = all_data["user"]["screen_name"]))
                        db.session.commit()
                        api.create_favorite(int(all_data["id"]))
                        user.trello_api.first().api_login().get_list(user.boards.first().column_id).add_card(f"{all_data['user']['name']}'s commission", f"Commission take on Twitter with the cyberplanificateur with this tweet : https://twitter.com/{all_data['user']['screen_name']}/status/{all_data['id']}")
                        print("found")
                        break
                break
        return True

    def on_error(self, status):
        print(status)

twitterStream = tweepy.Stream(auth, listener())
twitterStream.filter(follow=[str(api.me().id)])
