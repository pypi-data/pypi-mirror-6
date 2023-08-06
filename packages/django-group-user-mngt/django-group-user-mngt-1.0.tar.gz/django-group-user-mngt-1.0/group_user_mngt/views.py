# Create your views here.
import time
import os
import re
from datetime import datetime

from django.utils import timezone
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.core.context_processors import csrf
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings

#1. Test if Permission is granted
#--------------------------------

def user_has_access(request):
    '''
    Has current user user permission to change the groups/users ?
    '''
    user_query = User.objects.filter(username=str(request.user))
    perms = []
    if len(user_query) > 0 :
        perms = user_query[0].get_all_permissions()

    for perm in perms:
        if perm.find('change_user') > 0 :
            return True

    return False

#2. manage from group point of view (master is group, slave is user)
#------------------------------------------------------------------

def manage_groups(request):
    '''
    Main function for managing groups and the attached users
    '''

    if not user_has_access(request) :
        raise Http404

    print "s:", settings.GROUP_MANAGEMENT_TEMPLATE
    return render(request, settings.GROUP_MANAGEMENT_TEMPLATE,
                      {  },
                      context_instance=RequestContext(request))


@csrf_exempt
def ajax_gm_group_display(request):
    '''
    Function called by jquery jtable for displaying the configured group / user relationships
    '''
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    group_query_all = Group.objects.all()

    for group in group_query_all :
        adict = {}
        adict['Id'] = int(group.id)
        adict['name'] = group.name
        response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_user_display(request,gname):
    '''
    Function called by jquery jtable for displaying all users under a given group
    '''
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    group = Group.objects.get(name=gname)
    users = group.user_set.all()
    user_query_all = User.objects.all()

    for user in users :
        adict = {}
        adict['Id'] = str(user.id)
        adict['name'] = user.username
        adict['email'] = user.email
        adict['lastname'] = user.last_name
        adict['firstname'] = user.first_name
        adict['last_login'] = str(user.last_login)
        adict['date_joined'] = str(user.date_joined)
        adict['is_active'] = user.is_active
        adict['is_staff'] = user.is_staff
        adict['is_superuser'] = user.is_superuser
        response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


@csrf_exempt
def ajax_gm_group_update(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []


    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()

    adict = argsDict
    group = Group.objects.get(id=int(adict['Id']))
    group.name = adict['name']
    group.save()
    response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_group_add(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    already_there = True
    try:
        group = Group.objects.get(name=adict['name'])
    except Exception:
        already_there = False

    if already_there :
        response_dict['Result'] = 'ERROR'
        response_dict['Message'] = 'Group already exists in table'
    else :
        group = Group()
        group.name = adict['name']
        group.save()
        adict['Id'] = group.id
        response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_user_attach(request,gname):
    if not user_has_access(request) :
        return False

    print "attach:", gname
    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict
    g = Group.objects.get(name=gname)
    user = User.objects.get(username=adict['name'])
    g.user_set.add(user)

    adict['Id'] = str(user.id)
    adict['email'] = user.email
    adict['lastname'] = user.last_name
    adict['firstname'] = user.first_name
    adict['last_login'] = str(user.last_login)
    adict['date_joined'] = str(user.date_joined)
    adict['is_active'] = user.is_active
    adict['is_staff'] = user.is_staff
    adict['is_superuser'] = user.is_superuser

    response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_user_detach(request,gname):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    g = Group.objects.get(name=gname)
    user = User.objects.get(id=int(adict['Id']))
    g.user_set.remove(user)

    response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_user_index(request,gname):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Options'] = []

    group = Group.objects.get(name=gname)
    users = group.user_set.all()

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    all_users = User.objects.all()
    users = []
    for u in all_users:
        is_member = u.groups.filter(name=gname)
        if len(is_member) == 0 :
            users.append(u)


    for user in users :
        rec = {}
        rec['Value'] = str(user.username)
        rec['DisplayText'] = user.username
        response_dict['Options'].append(rec)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_gm_group_delete(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()

    adict = argsDict
    group = Group.objects.get(id=int(adict['Id']))
    group.delete()

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

#3. manage from user point of view (master is user, slave is group)
#------------------------------------------------------------------

def manage_users(request):
    '''
    Main function for managing groups and the attached users
    '''

    if not user_has_access(request) :
        raise Http404

    return render(request, settings.USER_MANAGEMENT_TEMPLATE,
                      {  },
                      context_instance=RequestContext(request))

@csrf_exempt
def ajax_um_user_display(request):
    '''
    Function called by jquery jtable for displaying the configured user / group relationships
    '''
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    user_query_all = User.objects.all()

    for user in user_query_all :
        adict = {}
        adict['Id'] = int(user.id)
        adict['email'] = user.email
        adict['active'] = user.is_active
        adict['lastname'] = user.last_name
        adict['firstname'] = user.first_name
        adict['is_staff'] = user.is_staff
        adict['is_superuser'] = user.is_superuser
        adict['last_login'] = str(user.last_login)
        adict['date_joined'] = str(user.date_joined)
        response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_group_display(request,uname):
    '''
    Function called by jquery jtable for displaying all groups under a given user
    '''
    if not user_has_access(request) :
        return False

    print "308:", uname
    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    user = User.objects.get(username=uname)
    groups = user.groups.values_list('name',flat=True)
    print user, groups
    for sel in groups :
        group = Group.objects.get(name=sel)
        adict = {}
        adict['Id'] = int(group.id)
        adict['name'] = group.name
        response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


@csrf_exempt
def ajax_um_user_update(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []


    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()

    adict = argsDict
    print adict
    user = User.objects.get(id=int(adict['Id']))
    user.email = adict['email']
    if adict.has_key('active') :
        user.is_active = adict['active']
    else :
        user.is_active = False
    if adict.has_key('password') :
        user.password = adict['password']
    if adict.has_key('lastname') :
        user.last_name = adict['lastname']
    if adict.has_key('firstname') :
        user.first_name = adict['firstname']
    if adict.has_key('is_staff') :
        user.is_staff = adict['is_staff']
    else :
        user.is_staff = False
    if adict.has_key('is_superuser') :
        user.is_superuser = adict['is_superuser']
    else :
        user.is_superuser = False

    user.save()
    response_dict['Records'].append(adict)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_user_add(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    already_there = True
    try:
        user = User.objects.get(email=adict['email'])
    except Exception:
        already_there = False

    if already_there :
        response_dict['Result'] = 'ERROR'
        response_dict['Message'] = 'User already exists in table'
    else :
        user = User()
        user.username = adict['email']
        user.email = adict['email']
        if adict.has_key('active') :
            user.is_active = adict['active']
        else :
            user.is_active = False
        if adict.has_key('password') :
            user.password = adict['password']
        if adict.has_key('is_superuser') :
            user.is_superuser = adict['is_superuser']
        else :
            user.is_superuser = False
        if adict.has_key('is_staff') :
            user.is_staff = adict['is_staff']
        else :
            user.is_staff = False
        if adict.has_key('firstname') :
            user.first_name = adict['firstname']
        if adict.has_key('lastname') :
            user.last_name = adict['lastname']
        user.date_joined = datetime.now()
        user.save()
        adict['Id'] = user.id
        response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_group_attach(request,uname):
    if not user_has_access(request) :
        return False

    print "attach:", uname
    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    user = User.objects.get(username=uname)
    g = Group.objects.get(name=adict['name'])

    g.user_set.add(user)

    adict['Id'] = str(g.id)
    adict['name'] = g.name

    response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_group_detach(request,uname):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict

    print uname
    print adict
    u = User.objects.get(username=uname)
    g = Group.objects.get(id=int(adict['Id']))
    g.user_set.remove(u)

    response_dict['Record'] = adict

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_group_index(request,uname):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Options'] = []

    user = User.objects.get(username=uname)

    #Get all groups a user belongs to
    #groups = user.groups.values_list('name',flat=True)
    groups = Group.objects.all()
    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()
    adict= argsDict


    for group in groups :
        is_member = user.groups.filter(name=group.name)
        if len(is_member) == 0 :
            rec = {}
            rec['Value'] = group.name
            rec['DisplayText'] = group.name
            response_dict['Options'].append(rec)

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@csrf_exempt
def ajax_um_user_delete(request):
    if not user_has_access(request) :
        return False

    response_dict = {}
    response_dict['Result'] = 'OK'
    response_dict['Records'] = []

    argsDict = dict(request.POST.iterlists())
    argsDict = request.POST.dict()

    adict = argsDict
    user = User.objects.get(id=int(adict['Id']))
    user.delete()

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
