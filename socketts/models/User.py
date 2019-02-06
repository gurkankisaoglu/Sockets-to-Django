from mongoengine import *


class User(Document):

    def __init__(self, username=None, groups=[], password=None, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.username = username
        self.groups = groups
        self.password = password
