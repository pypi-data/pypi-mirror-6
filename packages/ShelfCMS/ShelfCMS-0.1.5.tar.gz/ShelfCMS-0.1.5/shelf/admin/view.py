from flask_admin.contrib import sqla, fileadmin
from flask.ext.admin.base import expose

from shelf.admin.form.fields import LocalizedTextField, WysiwygTextField, LocalizedWysiwygTextField
from shelf.model.base import shelf_computed_models

import os
import os.path as op
from operator import itemgetter

from flask import request
from sqlalchemy.types import Text

from base64 import b64decode

from jinja2 import contextfunction
from flask.ext.admin.contrib.sqla import form

class ShelfModelView(sqla.ModelView):
    list_template = "shelf-admin/model/list.html"
    create_template = "shelf-admin/model/create.html"
    edit_template = "shelf-admin/model/edit.html"

    @contextfunction
    def get_list_value(self, context, model, name):
        if isinstance(getattr(model, name), shelf_computed_models()['LocalizedString']) \
              or isinstance(getattr(model, name), shelf_computed_models()['LocalizedText']):
            return getattr(model, name).value
        return super(ShelfModelView, self).get_list_value(context, model, name)

    def scaffold_form(self):
        cls = super(ShelfModelView, self).scaffold_form()
        for k, v in self.model.__dict__.items():
            if hasattr(v, "type") and isinstance(v.type, Text):
                setattr(cls, k, WysiwygTextField())

            if hasattr(v, "mapper"):
                if issubclass(v.mapper.class_, shelf_computed_models()['LocalizedString']) \
                    and not issubclass(self.model, shelf_computed_models()['LocalizedString']):
                        setattr(cls, k, LocalizedTextField())
                elif issubclass(v.mapper.class_, shelf_computed_models()['LocalizedText']) \
                    and not issubclass(self.model, shelf_computed_models()['LocalizedText']):
                        setattr(cls, k, LocalizedWysiwygTextField())

        return cls

from flask.ext.admin.helpers import get_form_data

class ShelfPageView(ShelfModelView):
    can_create = False
    can_delete = False
    
    def edit_form(self, obj=None):
        """
            Instantiate model editing form and return it.

            Override to implement custom behavior.
        """
        converter = self.model_form_converter(self.session, self)
        cls = form.get_form(obj.__class__, converter,
                                   base_class=self.form_base_class,
                                   only=self.form_columns,
                                   exclude=self.form_excluded_columns,
                                   field_args=self.form_args,
                                   extra_fields=self.form_extra_fields)

        if self.inline_models:
            cls = self.scaffold_inline_form_models(form_class)

        del cls.name

        mapper = obj._sa_class_manager.mapper
        properties = ((p.key, p) for p in mapper.iterate_properties)

        for k, v in properties:
            print k, v
            if hasattr(v, "type") and isinstance(v.type, Text):
                setattr(cls, k, WysiwygTextField())

            if hasattr(v, "mapper"):
                if issubclass(v.mapper.class_, shelf_computed_models()['LocalizedString']) \
                    and not issubclass(obj.__class__, shelf_computed_models()['LocalizedString']):
                        setattr(cls, k, LocalizedTextField())
                elif issubclass(v.mapper.class_, shelf_computed_models()['LocalizedText']) \
                    and not issubclass(obj.__class__, shelf_computed_models()['LocalizedText']):
                        setattr(cls, k, LocalizedWysiwygTextField())

        return cls(get_form_data(), obj=obj)

    def update_model(self, form, model):
        print form.data
        return super(ShelfPageView, self).update_model(form, model)


class ShelfFileAdmin(fileadmin.FileAdmin):
    list_template = "shelf-admin/file/list.html"
    iconic_template = "shelf-admin/file/iconic.html"
    upload_template = "shelf-admin/file/upload.html"

    @expose('/asyncupload', methods=("POST",))
    def async_upload(self):
        mfile = request.form['file']
        encoded = mfile.replace(' ', '+')
        decoded = b64decode(encoded)
        with open('tmp.jpg', 'w') as f:
            f.write(decoded)
        return "True"

    @expose('/icons/')
    @expose('/icons/b/<path:path>')
    def iconic_index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}
        mime_by_ext = {'text': ('.pdf', '.txt', '.doc', '.html', '.xml', '.css'),
                        'archive': ('.zip',),
                        'image': ('.png', '.jpg', '.jpeg'),
                        'video': ('.mpg', '.mpeg', '.wmv', '.mp4', '.flv', '.mov')
                        }

        # Parent directory
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

            items.append(('..', parent_path, True, 0))

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path):
                items.append((f, rel_path, op.isdir(fp), op.getsize(fp)))
                mimes[rel_path] = 'other'
                for mime in mime_by_ext:
                    if op.splitext(rel_path)[1] in mime_by_ext[mime]:
                        mimes[rel_path] = mime


        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.iconic_template,
                           dir_path=path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)

    @expose('/')
    @expose('/b/<path:path>')
    def index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}
        mime_by_ext = {'text': ('.pdf', '.txt', '.doc', '.html', '.xml', '.css'),
                        'archive': ('.zip',),
                        'image': ('.png', '.jpg', '.jpeg'),
                        'video': ('.mpg', '.mpeg', '.wmv', '.mp4', '.flv', '.mov')
                        }

        # Parent directory
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

            items.append(('..', parent_path, True, 0))

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path):
                items.append((f, rel_path, op.isdir(fp), op.getsize(fp)))
                mimes[rel_path] = 'other'
                for mime in mime_by_ext:
                    if op.splitext(rel_path)[1] in mime_by_ext[mime]:
                        mimes[rel_path] = mime


        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.list_template,
                           dir_path=path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)