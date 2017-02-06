from mongoengine import Document, fields


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
