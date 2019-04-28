import sqlite3

def tradd(id, token):
	with sqlite3.connect('database.db') as db:
		sucess = True
		dbc = db.cursor()
		for u in dbc.execute("SELECT * FROM trello WHERE id=?", (id,)):
			sucess = False
		if sucess:
			dbc.execute("INSERT INTO trello (id, token) VALUES (?, ?)", (id, token,))
		dbc.close()
		db.commit()
		return sucess

def trrm(id):
    with sqlite3.connect('database.db') as db:
        dbc = db.cursor()
        dbc.execute("DELETE FROM trello WHERE id=?", (id,))
        dbc.close()
        db.commit()

def trtoken(id):
	with sqlite3.connect('database.db') as db:
		token = False
		dbc = db.cursor()
		for u in dbc.execute("SELECT * FROM trello WHERE id=?;", (id,)):
			token = u
		dbc.close()
		return token

def twadd(user, id, maxslots, keywords):
	with sqlite3.connect('database.db') as db:
		dbc = db.cursor()
		dbc.execute("INSERT INTO tweets (user, id, slots, maxslots, keywords) VALUES (?, ?, ?, ?, ?)", (user, id, 0, maxslots, keywords,))
		dbc.close()
		db.commit()

def twrm(id):
	with sqlite3.connect('database.db') as db:
		dbc = db.cursor()
		dbc.execute("DELETE FROM tweets WHERE id=?", (id,))
		dbc.close()
		db.commit()

def twlist(user):
	with sqlite3.connect('database.db') as db:
		dbc = db.cursor()
		tweets = list()
		for u in dbc.execute("SELECT * FROM tweets WHERE user=?", (user,)):
			tweets.append({"id": u[1], "slots": u[2], "maxslots": u[3], "keywords": u[4]})
		dbc.close()
		db.commit()
	return tweets


with sqlite3.connect('database.db') as db:
	Table = False
	dbc = db.cursor()
	log = False
	iid = None
	for t in dbc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trello';"):
		Table = True
	if not Table:
			dbc.execute('''CREATE TABLE trello (id int, token text)''')
			dbc.execute('''CREATE TABLE tweets (user int, id int, slots int, maxslots int, keywords text)''')
			dbc.close()
			db.commit()
	#register("flifloo", "flifloo@gmail.com", "owo")
