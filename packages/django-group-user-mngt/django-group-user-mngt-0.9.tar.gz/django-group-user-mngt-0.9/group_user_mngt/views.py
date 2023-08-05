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

def manage_groups(request):
    '''
    Main function for managing groups and the attached users
    '''

    if not user_has_access(request) :
        raise Http404

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
    Function called by jquery jtable for displaying all article permissions
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
