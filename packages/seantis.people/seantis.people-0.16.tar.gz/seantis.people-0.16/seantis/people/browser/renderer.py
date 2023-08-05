""" Provides a fast renderer for schema fields. Since this renderer is used
on lists and tables and therefore called many times in a request the following
options were not chosen:

z3c.form display mode rendering - too complicated, hard to customize and slow
zpt templates - quite a bit slower because of features we don't need

The snippets rendered here so simple that string.Template can be used which
is by far the fastest way of doing templates in python.

"""

import string

from zope.schema import getFields, Text, Tuple, List, Set, FrozenSet
from plone.namedfile.field import NamedBlobImage, NamedImage
from plone.app.textfield import RichText
from plone.app.uuid.utils import uuidToCatalogBrain
from Products.ZCatalog.interfaces import ICatalogBrain

from seantis.plonetools.schemafields import Email, Website
from seantis.plonetools import tools

from seantis.people.utils import UUIDList


class EmailFieldRenderer(object):

    template = string.Template(u'<a href="mailto:${mail}">${mail}</a>')

    def __call__(self, context, field):
        mail = getattr(context, field)
        if mail:
            return self.template.substitute(mail=mail)
        else:
            return u''


class WebsiteFieldRenderer(object):

    template = string.Template(u'<a href="${url}" target="_blank">${url}</a>')

    def __call__(self, context, field):
        url = getattr(context, field)
        if url:
            return self.template.substitute(url=url)
        else:
            return u''


class TextRenderer(object):

    def __call__(self, context, field):
        return '<br />'.join(getattr(context, field, u'').splitlines())


class RichTextRenderer(object):

    def __call__(self, context, field):
        return getattr(context, field).output


class ListRenderer(object):

    def __call__(self, context, field):
        return u', '.join(getattr(context, field, tuple()))


class UUIDListRenderer(object):

    template = string.Template(u'<a href="${url}">${title}</a>')

    def __call__(self, context, field):
        uuids = getattr(context, field, None)

        if not uuids:
            return u''

        unicode_sortkey = tools.unicode_collate_sortkey()

        brains = (uuidToCatalogBrain(uid) for uid in uuids)
        items = sorted(
            ((b.getURL(), b.Title) for b in brains),
            key=lambda i: unicode_sortkey(i[1])
        )

        return ', '.join(
            self.template.substitute(url=url, title=title.decode('utf-8'))
            for url, title in items
        )


class ImageRenderer(object):

    template = string.Template(u'<img src="${url}" />')

    def __call__(self, context, field):
        img = getattr(context, field)
        if img:
            if ICatalogBrain.providedBy(context):
                baseurl = context.getURL()
            else:
                baseurl = context.absolute_url()

            url = '/'.join((baseurl, '@@images', field, 'thumb'))

            return self.template.substitute(url=url)
        else:
            return u''


# This is not the best way to match objects to classes, but it sure is the
# fastest. Checking through isinstance would require going through a list.
# Since that can easily happen more than a thousand times in a request it's
# better to be fast than to be right.
renderers = {
    Email: EmailFieldRenderer(),
    Website: WebsiteFieldRenderer(),
    NamedBlobImage: ImageRenderer(),
    NamedImage: ImageRenderer(),
    Text: TextRenderer(),
    RichText: RichTextRenderer(),
    Tuple: ListRenderer(),
    List: ListRenderer(),
    Set: ListRenderer(),
    FrozenSet: ListRenderer(),
    list: ListRenderer(),
    set: ListRenderer(),
    tuple: ListRenderer(),
    UUIDList: UUIDListRenderer(),
}


class Renderer(object):

    def __init__(self, schema, redirects=None):
        self.schema = schema
        self.fields = getFields(schema)
        self.redirects = redirects or {}

    def render(self, context, field):
        field = self.redirects.get(field, field)
        fieldtype = type(self.fields.get(field, getattr(context, field, None)))
        return renderers.get(fieldtype, getattr)(context, field)
