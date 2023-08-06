from __future__ import unicode_literals
from contextlib import closing
import os

from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from flatpages.model import DeclarativeBase, DBSession
from tgext.pluggable import app_model, primary_key, plug_url

from datetime import datetime
from tg import config
from tg.caching import cached_property
from flatpages.lib.formatters import FORMATTERS


class FlatPage(DeclarativeBase):
    __tablename__ = 'flatpages_page'

    uid = Column(Integer, autoincrement=True, primary_key=True)

    template = Column(Unicode(1024), nullable=False, default="genshi:flatpages.templates.page")
    slug = Column(Unicode(128), index=True, unique=True, nullable=False)
    title = Column(Unicode(512), nullable=False)
    content = Column(Unicode(64000), default='')
    required_permission = Column(Unicode(256), nullable=True, default=None)

    updated_at = Column(DateTime, nullable=False,
                        default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, nullable=False,
                        default=datetime.utcnow)

    author_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    author = relation(app_model.User)

    @classmethod
    def by_slug(cls, slug):
        return DBSession.query(cls).filter_by(slug=slug).first()

    @cached_property
    def url(self):
        return plug_url('flatpages', '/' + self.slug)

    @cached_property
    def html_content(self):
        format = config['_flatpages']['format']
        formatter = FORMATTERS[format]

        content = self.content
        if content.startswith('file://'):
            package_path = config['paths']['root']
            file_path = os.path.join(package_path, content[7:])
            with closing(open(file_path)) as f:
                content = f.read()

        return formatter(content)