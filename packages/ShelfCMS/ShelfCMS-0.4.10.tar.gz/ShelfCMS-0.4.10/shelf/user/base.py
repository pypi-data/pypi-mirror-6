import flask_login
from flask.ext.bcrypt import Bcrypt

login = None

class ShelfLoginManager(flask_login.LoginManager):
	shelf = None
	bcrypt = None

	def generate_password_hash(self, pw):
		return self.bcrypt.generate_password_hash(pw)

	def check_password_hash(self, pw_hash, pw):
		return self.bcrypt.check_password_hash(pw_hash, pw)

	def __init__(self, app=None, add_context_processor=True, shelf=None):
		if shelf:
			self.shelf = shelf
		super(ShelfLoginManager, self).__init__(app, add_context_processor)

	def init_app(self, app, add_context_processor=True):
		super(ShelfLoginManager, self).init_app(app, add_context_processor)
		self.bcrypt = Bcrypt(app)

login = ShelfLoginManager()