from __future__ import unicode_literals

from mongoengine import Document, fields
from mongoengine.python_support import StringIO
from PIL import Image


class ImageServer(Document):
    server_name = fields.StringField(required=True)
    server_ip = fields.StringField(required=True)

    def __str__ (self):
        return "%s(%s)" % (self.server_name, self.server_ip)


"""
We only save the path on local disk, rather than the image data into the database,
in order to reduce database memory cost. As a result, the image may be moved from
the saved path.
"""
class DBImage(Document):
    server = fields.ObjectIdField(required=True)
    path = fields.StringField(required=True)
    mime_type = fields.StringField(required=True)
    width = fields.IntField(required=True)
    height = fields.IntField(required=True)
    source = fields.StringField()
    meta = {
        'indexes': [
            {
                'fields': ['path'],
                'unique': True
            },
            '#source'
        ]
    }

    def get_thumbnail(self):
        try:
            my_thumbnail = DBImageThumbnail.objects.get(DBImage=self.pk)
            return my_thumbnail
        except DBImageThumbnail.DoesNotExist:
            im = Image.open(self.path)
            thumbnail_height = 200
            thumbnail_width = thumbnail_height * im.width / im.height
            im.thumbnail((thumbnail_width, thumbnail_height), Image.ANTIALIAS)
            io = StringIO()
            im.save(io, im.format)
            io.seek(0)

            my_thumbnail = DBImageThumbnail(DBImage=self.pk,
                                            file=io,
                                            width=thumbnail_width,
                                            height=thumbnail_height,
                                            mime_type=self.mime_type)
            my_thumbnail.save()
            return my_thumbnail


    def __str__(self):
        return "[%s](%s)" % (self.server, self.path)


"""
The thumbnails are directly saved into the GridFs in the database.
However, we only save a limited number of thumbnails as caches.
"""
class DBImageThumbnail(Document):
    DBImage = fields.ObjectIdField(required=True)
    file = fields.FileField(required=True)
    width = fields.IntField(required=True)
    height = fields.IntField(required=True)
    mime_type = fields.StringField(required=True)
    meta = {
        'max_documents': 200000,
        'indexes': [
            {
                'fields': ['DBImage'],
                'unique': True
            }
        ]
    }

