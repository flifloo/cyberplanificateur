import sqlite3

def tradd(id, token):
	with sqlite3.connect('database.db') as db:
		sucess = True
		dbc = db.cursor()
		for u in dbc.execute("SELECT * FROM trello WHERE id=?", (id,)):
			sucess = False
		if sucess:
			dbc.execute("INSERT INTO trello (id, token) VALUES (?, ?)", (id, token))
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

with sqlite3.connect('database.db') as db:
	Table = False
	dbc = db.cursor()
	log = False
	iid = None
	for t in dbc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trello';"):
		Table = True
	if not Table:
			dbc.execute('''CREATE TABLE trello (id text, token text)''')
			dbc.close()
			db.commit()
	#register("flifloo", "flifloo@gmail.com", "owo")
