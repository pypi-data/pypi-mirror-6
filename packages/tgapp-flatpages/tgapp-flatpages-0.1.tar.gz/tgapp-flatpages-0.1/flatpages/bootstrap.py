# -*- coding: utf-8 -*-
"""Setup the flatpages application"""
from __future__ import print_function

from flatpages import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print('Bootstrapping flatpages...')

    p = app_model.Permission(permission_name='flatpages', description='Can manage flat pages')
    model.DBSession.add(p)
    model.DBSession.flush()

    g = model.DBSession.query(app_model.Group).filter_by(group_name='managers').first()
    if g:
        g.permissions.append(p)
    model.DBSession.flush()

