from __future__ import unicode_literals

from mongoengine import Document, fields
import numpy as np
from django import forms
import datetime
from .utils import PasswordEncryption


class AnnoQuery(Document):
    query_image_id = fields.ObjectIdField()
    target_image_ids = fields.ListField(fields.ObjectIdField())
    meta = {
        'indexes': [
            {
                'fields': ['query_image_id'],
                'unique': True
            }
        ]
    }

    def __str__(self):
        return str(self.id)


class AnnoUser(Document):
    user_name = fields.StringField(required=True)
    __password = fields.StringField(required=True)
    annotation_list = fields.ListField(fields.ReferenceField(AnnoQuery))
    label_index = fields.IntField(default=-1)
    meta = {
        'indexes': ['#user_name']
    }

    def set_password(self, password):
        encrypt = PasswordEncryption()
        self.__password = encrypt.get_password(password)

    def validate_password(self, password):
        encrypt = PasswordEncryption()
        return encrypt.validate(password, self.__password)

    def clean(self):
        if self.label_index == -1:
            queries = AnnoQuery.objects.all()
            perm = np.random.permutation(len(queries))
            number = len(queries)
            self.annotation_list = []
            perm_list = perm[:number].tolist()
            for id in range(number):
                self.annotation_list.append(queries[perm_list[id]])
            self.label_index = 0

    @property
    def current_annotation_id(self):
        return self.annotation_list[self.label_index].id

    @property
    def current_query_id(self):
        return self.annotation_list[self.label_index].query_image_id

    @property
    def current_annotation(self):
        return self.annotation_list[self.label_index].target_image_ids

    @property
    def completed(self):
        return self.label_index >= len(self.annotation_list)


class AnnoAnnotation(Document):
    user = fields.ObjectIdField()
    query = fields.ObjectIdField()
    scores = fields.ListField(fields.FloatField())
    date = fields.DateTimeField(default=datetime.datetime.now)
    meta = {
        'indexes': ['#user','#query']
    }

class SimpleTest(Document):
    scores = fields.ListField(fields.ObjectIdField())


class LoginForm(forms.Form):
    user_name = forms.CharField(label='User Name', min_length=3)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', min_length=3)


class RegisterForm(forms.Form):
    user_name = forms.CharField(label='User Name')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', min_length=3)
    password_cfm = forms.CharField(widget=forms.PasswordInput(), label='Repeat Password', min_length=3)


class AnnotateForm(forms.Form):
    query_id = forms.CharField(min_length=24, max_length=24)
    scores = forms.CharField()