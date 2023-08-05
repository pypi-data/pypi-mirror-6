from flask.ext.admin import Admin
from flask import Blueprint, render_template

from flask.ext.admin.base import expose, AdminIndexView

class ShelfIndexView(AdminIndexView):
    @expose('/login/')
    def login(self):
        return render_template("shelf-admin/login.html")

class ShelfAdmin(Admin):
    def __init__(self, app=None, name=None,
                 url=None, subdomain=None,
                 index_view=None,
                 translations_path=None,
                 endpoint=None,
                 static_url_path=None,
                 base_template=None):
        if base_template is None:
            base_template = "shelf-admin/base.html"
        if index_view is None:
            index_view = ShelfIndexView(endpoint=endpoint, url=url)
        super(ShelfAdmin, self).__init__(app, name, url, subdomain, 
            index_view, translations_path, 
            endpoint, static_url_path, base_template)

    def _init_extension(self):
        super(ShelfAdmin, self)._init_extension()
        shelf_admin = Blueprint('shelf', 'shelf', url_prefix="/shelf", 
            template_folder="templates", static_folder="static")
        self.app.register_blueprint(shelf_admin)
    
    