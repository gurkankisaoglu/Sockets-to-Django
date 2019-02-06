import cv2
import datetime
import pickle
from django.template.defaultfilters import linebreaksbr, urlize, register
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render
import json
from img_tool_app.forms import addGroupForm, deleteForm, updatePassForm, loadImageForm, saveImageForm, setDefaultForm, \
    addRuleForm,loadFromDB
from .forms import loginForm, addUserForm
from .models import User, Group, Image
from django.http import JsonResponse
import numpy
from PIL import Image as PILImage
from io import BytesIO
from base64 import b64encode


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
    if 'currentUser' in request.session:
        allUsers = User.objects.all()
        successful_event = False
        form = addUserForm.addUserForm()
        formDel = deleteForm.deleteForm()
        formUpdatePass = updatePassForm.updatePassForm()

        if request.method == 'POST':
            method = request.POST.get("action")

            if method == 'goBack':  # not implemented
                successful_event = True

            if method == "addUser":
                username = request.POST.get("username")
                password = request.POST.get("password")
                groupList = request.POST.get("groups")
                groupList = json.loads(groupList)
                User.addUser(username, groupList, password)
                successful_event = True
            if method == "delUser":
                name = request.POST.get("username")
                User.delUser(name)
                successful_event = True

            if method == "updatePass":
                formUpdatePass = updatePassForm.updatePassForm(request.POST)
                if formUpdatePass.is_valid():
                    newPass = request.POST.get("newPassword")
                    User.setPassword(request.session['currentUser'], newPass)
                    successful_event = True

            json_to_client = {'isSuccessful': successful_event}
            return JsonResponse(json_to_client)
        if request.method == 'GET':
            return render(request, 'user.html',
                          {'allUsers': allUsers, 'form': form, 'formDel': formDel, 'formUpdatePass': formUpdatePass,
                           'session': request.session})

    else:  # not logged in
        return HttpResponseRedirect(redirect_to='/login/')


def image(request):
    if 'currentUser' in request.session:
        allImages = Image.objects.all()
        form = loadImageForm.loadImageForm()
        formSave = saveImageForm.saveImageForm()
        formLoad = loadFromDB.loadImageForm()
        formSetDefault = setDefaultForm.setDefaultForm()
        formAddRule = addRuleForm.addRuleForm()
        formDelRule = deleteForm.deleteForm()
        successful_event = False
        if request.method == 'POST':
            method = request.POST.get("action")
            print (request.POST)
            if method == 'goBack':
                successful_event = True
            if method == "loadFromComp":
                img = request.POST.get('img')
                adjustSession(request, False, img)
                successful_event = True
            if method == "save":
                imgInstance = Image(owner=request.session['currentUser'], name=request.POST.get('imageName'),
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                imgInstance.saveDB(imgInstance.name)
                successful_event = request.session['currentUser']
            if method == "loadDB":
                nameToLoaded = request.POST.get('imageName')
                imgInstance = Image.objects.filter(name=nameToLoaded)[0]
                imgInstance.load(nameToLoaded)
                adjustSession(request, True, imgInstance)
                successful_event = True
            if method == 'showImage':
                imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                img = imgInstance.getImage(request.session['currentUser'])
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pilimg = PILImage.fromarray(img)
                pilimg.save("img_tool_app/media/trial_image.jpeg",'JPEG')
                return HttpResponse("/media/trial_image.jpeg",content_type="text/plain")
            if method == 'set default':
                imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                imgInstance.setDefault(request.POST.get('defaultAction'))
                adjustSession(request, True, imgInstance)
                img = imgInstance.getImage(request.session['currentUser'])
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pilimg = PILImage.fromarray(img)
                pilimg.save("img_tool_app/media/trial_image.jpeg", 'JPEG')
                print("New Image with new Default Saved")
                return HttpResponse("/media/trial_image.jpeg", content_type="text/plain")

            if method == 'add rule':
                print ("helo")
                imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                effects = request.POST.get('effects')
                action = request.POST.get('defaultAction')
                shape = request.POST.get('shape')
                coordinates = request.POST.get('coordinates').split(' ')
                rule = None
                print (shape)
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
                img = imgInstance.getImage(request.session['currentUser'])
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pilimg = PILImage.fromarray(img)
                pilimg.save("img_tool_app/media/trial_image.jpeg", 'JPEG')
                print("New Image Saved")
                return HttpResponse("/media/trial_image.jpeg", content_type="text/plain")
            if method == 'delete rule':
                imgInstance = Image(owner=request.session['owner'], name=request.session['name'],
                                    rule_list=request.session['rule_list'],
                                    defaultAction=request.session['defaultAction'],
                                    is_initialized=request.session['is_initialized'],
                                    img=request.session['currentImage'])
                deletePos = request.POST.get('position')
                imgInstance.delRule(deletePos)
                request.session['owner'] = imgInstance.owner
                request.session['name'] = imgInstance.name
                request.session['defaultAction'] = imgInstance.defaultAction
                request.session['rule_list'] = imgInstance.rule_list
                request.session['is_initialized'] = imgInstance.is_initialized
                request.session['currentImage'] = imgInstance.img.name
                img = imgInstance.getImage(request.session['currentUser'])
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pilimg = PILImage.fromarray(img)
                pilimg.save("img_tool_app/media/trial_image.jpeg", 'JPEG')
                return HttpResponse("/media/trial_image.jpeg", content_type="text/plain")
            json_to_client = {'isSuccessful': successful_event}
            return JsonResponse(json_to_client)
        if request.method == 'GET':
            return render(request, 'image.html',
                          {'allImages': allImages, 'form': form, 'formSave': formSave, 'formLoadFromDB': formLoad,
                           'formSetDefault': formSetDefault, 'formAddRule': formAddRule, 'formDelRule': formDelRule,
                           'session': request.session})


    else:  # not logged in
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
    if 'currentUser' in request.session:
        allGroups = Group.objects.all()
        successful_event = False
        form = addGroupForm.addGroupForm()
        formDel = deleteForm.deleteForm()

        if request.method == 'POST':
            method = request.POST.get("action")

            if method == 'goBack':  # not implemented
                successful_event = True

            if method == "addGroup":
                groupname = request.POST.get("groupname")
                Group.addGroup(groupname)
                successful_event = True

            if method == "delGroup":
                name = request.POST.get("name")
                Group.delGroup(name)
                successful_event = True

            json_to_client = {'isSuccessful': successful_event}
            return JsonResponse(json_to_client)
        if request.method == 'GET':
            return render(request, 'group.html', {'allGroups': allGroups, 'form': form, 'formDel': formDel,
                                              'session': request.session})

    else:  # not logged in
        return HttpResponseRedirect(redirect_to='/login/')

@register.filter
def getGroupsOfUser(username):
    return User.getGroups(username)


@register.filter
def getUsersOfGroup(group):
    return Group.getUsers(group)
