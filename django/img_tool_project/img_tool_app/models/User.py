from djongo import models


class User(models.Model):
    username = models.CharField(unique=True, max_length=24)
    password = models.CharField(max_length=16)
    groups = models.ListField()

    def __str__(self):
        return self.username

    @classmethod
    def checkLogin(cls, username, password):
        if not User.objects.filter(username=username, password=password).exists():
            return None
        return User.objects.filter(username=username, password=password).first()

    @classmethod
    def getGroups(cls, name):
        # get groups which user belongs to
        result = User.objects.filter(username=name).first()
        if result:
            return result.groups
        return None

    @classmethod
    def addUser(cls, name, groups, password):
        maxId = 1
        if User.objects.all().order_by("-id"):
            maxId = User.objects.all().order_by("-id")[0].id + 1
        User.objects.create(id=maxId, username=name, groups=groups,
                            password=password)
        from ..models import Group

        for group in groups:
            willUpdate = Group.objects.get(groupname=group)
            userList = willUpdate.users_in_list
            userList.append(name)
            willUpdate.users_in_list = userList
            willUpdate.save()

    @classmethod
    def delUser(cls, name):
        groupsOfUser = User.objects.get(username=name).groups
        User.objects.filter(username=name).delete()
        from ..models import Group

        for group in groupsOfUser:
            DBGroup = Group.objects.get(groupname=group)
            if DBGroup:
                DBGroup.users_in_list.remove(name)
                DBGroup.save()

    @classmethod
    def setPassword(cls, username, password):
        user = User.objects.get(username=username)
        user.password = password
        user.save()

    @classmethod
    def ismember(cls, username, group):
        # is member of a group
        user = User.objects.get(username=username)
        groups = user.groups
        if group in groups:
            return True
        return False

    @classmethod
    def regexsearch(cls,user, regex):
        # if user exists in result of regexsearch return true
        result = User.objects.filter(username__regex=regex)
        if user in result:
            return True
        return False

    @classmethod
    def ownsImage(self, username, imagename):
        from ..models import Image
        img = Image.objects.get(owner=username,name=imagename)
        if not img:
            return False
        return True
