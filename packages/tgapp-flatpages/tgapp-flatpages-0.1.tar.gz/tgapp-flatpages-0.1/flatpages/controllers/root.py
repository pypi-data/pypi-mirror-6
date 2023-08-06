# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController, predicates, config, abort, override_template, tmpl_context
from tg import expose, flash, require, url, lurl, request, redirect, validate
from tg.caching import cached_property
from tgext.crud import EasyCrudRestController
from tgext.pluggable import primary_key, app_model, plug_url
from tw2.core import Deferred
from tw2.forms import SingleSelectField, TextField

from flatpages import model
from flatpages.model import DBSession

from tgext.admin.layouts import BootstrapAdminLayout as BTLayout
from tgext.crud.resources import crud_script, CSSSource


class ManageController(EasyCrudRestController):
    allow_only = predicates.has_permission('flatpages')
    title = "Manage FlatPages"
    model = model.FlatPage
    crud_resources = [crud_script,
                      CSSSource(location='headbottom',
                                src='''
    .crud-sidebar .active {
        font-weight: bold;
        border-left: 3px solid #eee;
    }

    @media (max-width: 991px) {
        .pull-sm-right {
            float: right;
        }
    }

    @media (min-width: 992px) {
        .pull-md-right {
            float: right;
        }
    }
    ''')]

    # Helpers to retrieve form data
    _get_current_user = lambda: getattr(request.identity['user'], primary_key(app_model.User).key)
    _get_templates = lambda: config['_flatpages']['templates']
    _get_permissions = lambda: [('public', 'Public'), ('not_anonymous', 'Only Registered Users')] + \
                               DBSession.query(app_model.Permission.permission_name,
                                               app_model.Permission.description).all()

    FORM_OPTIONS = {
        '__entity__': model,
        '__hide_fields__': ['author'],
        '__omit_fields__': ['uid', '_id', 'updated_at', 'created_at'],
        '__field_order__': ['slug', 'title', 'template', 'required_permission'],
        '__field_widget_types__': {'template': SingleSelectField,
                                   'slug': TextField,
                                   'title': TextField,
                                   'required_permission': SingleSelectField},
        '__field_widget_args__': {'author': {'value': Deferred(_get_current_user)},
                                  'required_permission': {'prompt_text': None,
                                                          'options': Deferred(_get_permissions)},
                                  'content': {'rows': 20},
                                  'template': {'prompt_text': None,
                                               'options': Deferred(_get_templates)}}
    }

    TABLE_OPTIONS = {
        '__entity__': model,
        '__omit_fields__': ['_id', 'uid', 'author_id', 'created_at', 'template'],
    }

    # Configure look&feel according to Bootstrap3 admin theme
    table_type = type('TType', (BTLayout.TableBase,), TABLE_OPTIONS)
    table_filler_type = type('TFType', (BTLayout.TableFiller,), {'__entity__': model})
    edit_form_type = type('EFType', (BTLayout.EditableForm,), FORM_OPTIONS)
    new_form_type = type('NFType', (BTLayout.AddRecordForm,), FORM_OPTIONS)

    @property
    def mount_point(self):
        return plug_url('pages', '/manage')

    def _before(self, *args, **kw):
        super(ManageController, self)._before(*args, **kw)

        if request.response_type not in ('text/html', None):
            abort(406, 'Only HTML is supported')

    @expose(inherit=True)
    def get_all(self, *args, **kw):
        override_template(self.get_all, 'genshi:flatpages.templates.manage')
        return super(ManageController, self).get_all(*args, **kw)


class RootController(TGController):
    CACHE_EXPIRE = 7*86400  # 7 Days

    @expose()
    def _default(self, page=None, *args, **kw):
        page = model.FlatPage.by_slug(page)
        if page is None:
            abort(404, 'Page not found')

        permission = page.required_permission
        if permission and permission != 'public':
            if permission == 'not_anonymous':
                predicate = predicates.not_anonymous()
            else:
                predicate = predicates.has_permission(permission)

            if not predicate.is_met(request.environ):
                abort(403, 'Forbidden')

        override_template(RootController._default, page.template)
        return dict(page=page,
                    tg_cache={'expire': self.CACHE_EXPIRE,
                              'key': '%s-%s' % (page.slug, page.updated_at)})

    @cached_property
    def manage(self):
        return ManageController(DBSession.wrapped_session)