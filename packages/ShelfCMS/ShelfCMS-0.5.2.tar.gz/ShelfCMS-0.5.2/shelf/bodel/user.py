from model import db

class User:
	email = db.Column(db.String(255))
	first_name = db.Column(db.String(50))
	last_name = db.Column(db.String(50))
	password_hash = db.Column(db.String(60))
	active = db.Column(db.Boolean)
	role = db.Column(db.Enum("Super-Admin", "Admin", "Editor", "Author", "Contributor", "Subscriber"))