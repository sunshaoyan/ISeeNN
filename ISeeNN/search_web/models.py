from mongoengine import Document, fields
from django import forms

# Create your models here.


class Feature(Document):
    image = fields.ObjectIdField(required=True)
    dimension = fields.IntField(required=True)
    data = fields.BinaryField(required=True)
    model = fields.StringField(required=True)
    identity = fields.StringField(required=True)
    meta = {
        'indexes': [
            '#identity',
            {
                'fields': ['image', 'identity'],
                'unique': True
            }
        ]
    }


class ImageServer(Document):
    server_name = fields.StringField(required=True)
    server_ip = fields.StringField(required=True)

    def __str__(self):
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


class UserUploadImage(Document):
    data = fields.ImageField(required=True, size=(1024, 1024), thumbnail_size=(640, 200))
    feature = fields.BinaryField()
    identity = fields.StringField()


class ImageUploadForm(forms.Form):
    image_file = forms.ImageField()

