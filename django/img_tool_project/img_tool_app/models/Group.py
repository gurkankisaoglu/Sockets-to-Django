from djongo import models
from .User import User


class Group(models.Model):
    groupname = models.CharField(max_length=24, unique=True)
    users_in_list = models.ListField()

    def __str__(self):
        return self.groupname

    @classmethod
    def getUsers(cls, group):
        # get users which group have
        results = []
        users_list = User.objects.all()
        for user in users_list:
            if group in user.groups:
                results.append(user.username)
        return results

    @classmethod
    def addGroup(cls, name):
        # add group to db
        maxId = 1
        if Group.objects.all().order_by("-id"):
            maxId = Group.objects.all().order_by("-id")[0].id + 1
        Group.objects.create(id=maxId, groupname=name, users_in_list=[])

    @classmethod
    def delGroup(cls, groupname):
        users = User.objects.all()
        for user in users:
            if groupname in user.groups:
                user.groups.remove(groupname)
                user.save()

        from ..models import Group
        Group.objects.filter(groupname=groupname).delete()
