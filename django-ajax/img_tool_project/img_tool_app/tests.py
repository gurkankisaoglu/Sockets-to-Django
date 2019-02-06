from django.test import TestCase

# Create your tests here.
from img_tool_app.models import User, Group, Image

User.objects.all().delete()
Group.objects.all().delete()
Image.objects.all().delete()
User.addUser('admin', [], 'admin')