from flask import Blueprint
import model
import admin
import cache

class Shelf:
    def __init__(self, app):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        self.blueprint = Blueprint('shelf', 'shelf', url_prefix="/shelf", 
            template_folder="templates", static_folder="static")
        app.register_blueprint(self.blueprint)

        db = model.db
        model.db.init_app(app)
        model.db.app = app
        self.db = db 

        self.admin = admin.ShelfAdmin(app, shelf=self)

        self.cache = cache.ShelfCache(app, shelf=self)

        '''shelf_admin = Blueprint('shelf', 'shelf', url_prefix="/shelf", 
            template_folder="templates", static_folder="static")
        self.app.register_blueprint(shelf_admin)
        login_manager.init_app(self.app)
        login_bcrypt.init_app(self.app)
        db.init_app(self.app)
        db.app = self.app
        prepare_model(shelf_computed_model('User'))
        db.create_all()'''



'''

'''