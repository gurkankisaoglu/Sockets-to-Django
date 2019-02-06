from django.contrib import admin
from .models import User,Group,Image

admin.site.register(User)
admin.site.register(Image)
admin.site.register(Group)