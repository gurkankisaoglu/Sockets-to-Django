import cv2

from django.template.defaultfilters import linebreaksbr, urlize, register
from django.http import HttpResponseRedirect
from django.shortcuts import render

from img_tool_app.forms import addGroupForm, deleteForm, updatePassForm, loadImageForm, saveImageForm, setDefaultForm, \
    addRuleForm
from .forms import loginForm, addUserForm
from .models import User, Group, Image


# Create your views here.
def login(request):
    if 'currentUser' in request.session:
        return HttpResponseRedirect(redirect_to='/index/')
    form = loginForm.loginForm()
    if request.method == 'POST':
        form = loginForm.loginForm(request.POST)
        if form.is_valid():
            res = User.checkLogin(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if res:
                request.session['currentUser'] = res.username
                request.session['rule_list'] = []
                request.session['defaultAction'] = 'ALLOW'
                request.session['owner'] = res.username
                request.session['img'] = None
                request.session['is_initialized'] = False


                return HttpResponseRedirect(redirect_to='/index/')
    return render(request, 'login.html', {'form': form})


def index(request):
    if 'currentUser' in request.session:
        return render(request, 'index.html')
    return HttpResponseRedirect(redirect_to='/login/')


def user(request):
    allUsers = User.objects.all()
    if 'currentUser' in request.session:
        form = addUserForm.addUserForm()
        formDel = deleteForm.deleteForm()
        formUpdatePass = updatePassForm.updatePassForm()
        if request.method == 'POST':
            method = request.POST.get("goBack", '').lower()
            if method == 'go back':
                return render(request, 'index.html')
            method = request.POST.get("addUser", '').lower()
            if method == "add user":
                form = addUserForm.addUserForm(request.POST)
                if form.is_valid():
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    groupList = form.cleaned_data['groups']
                    User.addUser(username, groupList, password)
            method = request.POST.get("delUser", '').lower()
            if method == "delete user":
                formDel = deleteForm.deleteForm(request.POST)
                if formDel.is_valid():
                    name = formDel.cleaned_data['name']
                    User.delUser(name)
            method = request.POST.get("updatePass", '').lower()
            if method == "update":
                formUpdatePass = updatePassForm.updatePassForm(request.POST)
                if formUpdatePass.is_valid():
                    newPass = formUpdatePass.cleaned_data['newPassword']
                    User.setPassword(request.session['currentUser'], newPass)

        return render(request, 'user.html',
                      {'allUsers': allUsers, 'form': form, 'formDel': formDel, 'formUpdatePass': formUpdatePass,
                       'session': request.session})

    return HttpResponseRedirect(redirect_to='/login/')


def image(request):
    allImages = Image.objects.all()
    if 'currentUser' in request.session:
        form = loadImageForm.loadImageForm()
        formSave = saveImageForm.saveImageForm()
        formLoad = saveImageForm.saveImageForm()
        formSetDefault = setDefaultForm.setDefaultForm()
        formAddRule = addRuleForm.addRuleForm()
        formDelRule = deleteForm.deleteForm()
        if request.method == 'POST':
            method = request.POST.get("goBack", '').lower()
            if method == 'go back':
                return render(request, 'index.html')
            method = request.POST.get("load", '').lower()
            if method == "load":
                form = loadImageForm.loadImageForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data['img'].name
                    adjustSession(request, False, img)
            method = request.POST.get("save", '').lower()
            if method == "save":
                formSave = saveImageForm.saveImageForm(request.POST)
                if formSave.is_valid():
                    imgInstance = Image(owner=request.session['currentUser'], name=formSave.cleaned_data['imageName'],
                                        rule_list=request.session['rule_list'],
                                        defaultAction=request.session['defaultAction'],
                                        is_initialized=request.session['is_initialized'],
                                        img=request.session['currentImage'])
                    imgInstance.name = formSave.cleaned_data['imageName']
                    imgInstance.saveDB(imgInstance.name)
            method = request.POST.get("loadDB", '').lower()
            if method == "load":
                formLoad = saveImageForm.saveImageForm(request.POST)
                if formLoad.is_valid():
                    nameToLoaded = formLoad.cleaned_data['imageName']
                    imgInstance = Image.objects.filter(name=nameToLoaded)[0]
                    imgInstance.load(nameToLoaded)
                    adjustSession(request, True, imgInstance)
            method = request.POST.get("showImage", '').lower()
            if method == 'show image':
                imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                img = imgInstance.getImage(request.session['currentUser'])
                cv2.imshow('im', img)
                cv2.waitKey()
            method = request.POST.get("setDefault", '').lower()
            if method == 'set default':
                formSetDefault = setDefaultForm.setDefaultForm(request.POST)
                if formSetDefault.is_valid():
                    imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                        rule_list=request.session['rule_list'],
                                        defaultAction=request.session['defaultAction'],
                                        is_initialized=request.session['is_initialized'],
                                        img=request.session['currentImage'])
                    imgInstance.setDefault(formSetDefault.cleaned_data['defaultAction'])
                    adjustSession(request, True, imgInstance)
            method = request.POST.get("addRule", '').lower()
            if method == 'add rule':
                formAddRule = addRuleForm.addRuleForm(request.POST)
                if formAddRule.is_valid():
                    imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                        rule_list=request.session['rule_list'],
                                        defaultAction=request.session['defaultAction'],
                                        is_initialized=request.session['is_initialized'],
                                        img=request.session['currentImage'])
                    effects = formAddRule.cleaned_data['effects']
                    action = formAddRule.cleaned_data['action']
                    shape = formAddRule.cleaned_data['shape']
                    coordinates = formAddRule.cleaned_data['coordinates'].split(' ')
                    rule = None
                    if shape.lower() == 'circle':
                        rule = (shape, int(coordinates[0]), int(coordinates[1]), int(coordinates[2]))
                    if shape.lower() == 'rectangle':
                        rule = (
                            shape, int(coordinates[0]), int(coordinates[1]), int(coordinates[2]), int(coordinates[2]))
                    if shape.lower() == 'polyline':
                        coordinates = list(map(int, coordinates))
                        res = []
                        for i in range(0, len(coordinates), 2):
                            res.append((coordinates[i], coordinates[i + 1]))
                        rule = (shape, res)
                    imgInstance.addRule(effects, rule, action)
                    request.session['owner'] = imgInstance.owner
                    request.session['name'] = imgInstance.name
                    request.session['defaultAction'] = imgInstance.defaultAction
                    request.session['rule_list'] = imgInstance.rule_list
                    request.session['is_initialized'] = imgInstance.is_initialized
                    request.session['currentImage'] = imgInstance.img.name
            method = request.POST.get("delRule", '').lower()
            if method == 'delete rule':
                formDelRule = deleteForm.deleteForm(request.POST)
                if formDelRule.is_valid():
                    imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                        rule_list=request.session['rule_list'],
                                        defaultAction=request.session['defaultAction'],
                                        is_initialized=request.session['is_initialized'],
                                        img=request.session['currentImage'])
                    deletePos = formDelRule.cleaned_data['name']
                    imgInstance.delRule(deletePos)
                    request.session['owner'] = imgInstance.owner
                    request.session['name'] = imgInstance.name
                    request.session['defaultAction'] = imgInstance.defaultAction
                    request.session['rule_list'] = imgInstance.rule_list
                    request.session['is_initialized'] = imgInstance.is_initialized
                    request.session['currentImage'] = imgInstance.img.name

        return render(request, 'image.html',
                      {'allImages': allImages, 'form': form, 'formSave': formSave, 'formLoadFromDB': formLoad,
                       'formSetDefault': formSetDefault, 'formAddRule': formAddRule, 'formDelRule': formDelRule,
                       'session': request.session})

    return HttpResponseRedirect(redirect_to='/login/')


def adjustSession(request, isLoadedFromDB, item):
    if isLoadedFromDB:
        request.session['owner'] = item.owner
        request.session['name'] = item.name
        request.session['defaultAction'] = item.defaultAction
        request.session['rule_list'] = item.rule_list
        request.session['is_initialized'] = item.is_initialized
        request.session['currentImage'] = item.img.name
    else:
        request.session['owner'] = request.session['currentUser']
        request.session['name'] = 'defaultName'
        request.session['defaultAction'] = 'ALLOW'
        request.session['rule_list'] = []
        request.session['is_initialized'] = True
        request.session['currentImage'] = item


def group(request):
    allGroups = Group.objects.all()
    if 'currentUser' in request.session:
        method = request.POST.get("goBack", '').lower()
        if method == 'go back':
            return render(request, 'index.html')
        form = addGroupForm.addGroupForm()
        formDel = deleteForm.deleteForm()
        if request.method == 'POST':
            method = request.POST.get("addGroup", '').lower()
            if method == "add group":
                form = addGroupForm.addGroupForm(request.POST)
                if form.is_valid():
                    groupname = form.cleaned_data['groupname']
                    Group.addGroup(groupname)
            else:
                method = request.POST.get("delGroup", '').lower()
                if method == "delete group":
                    formDel = deleteForm.deleteForm(request.POST)
                    if formDel.is_valid():
                        name = formDel.cleaned_data['name']
                        Group.delGroup(name)
        return render(request, 'group.html', {'allGroups': allGroups, 'form': form, 'formDel': formDel,
                                              'session': request.session})

    return HttpResponseRedirect(redirect_to='/login/')


@register.filter
def getGroupsOfUser(username):
    return User.getGroups(username)


@register.filter
def getUsersOfGroup(group):
    return Group.getUsers(group)
