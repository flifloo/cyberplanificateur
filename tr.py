import trello
import tw

def is_trlogin(session):
    return is_twkeys(session) and database.trtoken(tw.api_login(session).me().id)
