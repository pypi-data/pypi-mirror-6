import re
from datetime import datetime

from markdown import Markdown

from sqlalchemy import event
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, DateTime, String, Text

from .base import Base, BaseMixin, TimestampMixin


slug_re = re.compile(r'^[\w-]+$')


class Entry(Base, BaseMixin, TimestampMixin):

    slug = Column(String(length=100), nullable=False, unique=True)
    title = Column(String(length=100), nullable=False)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=False)
    is_page = Column(Boolean, default=False)
    published = Column(Boolean, default=False)
    published_at = Column(DateTime)


@event.listens_for(Entry.slug, 'set')
def on_set_slug(entry, value, *_):
    if not slug_re.search(value):
        raise ValueError('Slug may contain only word characters and dash')


@event.listens_for(Entry.content, 'set')
def set_content_html(entry, value, *_):
    """Set content_html from content whenever content is set."""
    entry.content_html = Markdown().convert(value)


@event.listens_for(Entry.published, 'set')
def on_set_published(entry, published, already_published, _):
    if not published:
        entry.published_at = None
    elif not already_published:
        entry.published_at = datetime.now()
