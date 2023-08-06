# -*- coding: utf-8 -*-
"""The tgapp-flatpages package"""
import tg


def plugme(app_config, options):
    config = {'templates': options.get('templates', [('genshi:flatpages.templates.page', 'default')]),
              'format': options.get('format', 'rst')}
    tg.config['_flatpages'] = config
    return dict(appid='pages', global_helpers=False)