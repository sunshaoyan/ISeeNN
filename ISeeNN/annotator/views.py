from django.shortcuts import render, reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
import random
import numpy as np
from bson import ObjectId
import json

# Create your views here.

from search_web.models import Feature
from search_web.views import get_results, get_index_id, get_index_count
from .models import AnnoQuery, AnnoUser, AnnoAnnotation
from .models import LoginForm, RegisterForm, AnnotateForm

def authorize_user(func):
    def _authorize_user(request, *args, **kwargs):
        anno_user_id = request.session.get('anno_user_id', False)
        if not anno_user_id:
            return HttpResponseRedirect(reverse('annotator:login'))
        try:
            anno_user = AnnoUser.objects.get(id=anno_user_id)
            request.session['user_name'] = anno_user.user_name
            try:
                ret = func(request, *args, **kwargs)
                return ret
            finally:
                del request.session['user_name']
        except AnnoUser.DoesNotExist:
            return HttpResponseRedirect(reverse('annotator:login'))
    return _authorize_user


def authorize_admin(func):
    def _authorize_admin(request, *args, **kwargs):
        anno_user_name = request.session.get('user_name', False)
        if anno_user_name != 'admin':
            return HttpResponseForbidden('You do not have authority to visit this page')
        ret = func(request, *args, **kwargs)
        return ret
    return _authorize_admin


@authorize_user
@authorize_admin
def select(request, image_id=None):
    if image_id is None:
        count = get_index_count()
        idx = random.randint(0, count-1)
        image_id = get_index_id(idx)
    feature = Feature.objects.get(identity=settings.FEATURE_IDENTITY, image=image_id)
    query_feat = np.frombuffer(feature.data, dtype='float32')
    results = get_results(query_feat)
    return render(request, 'annotator/select.html', {
        'query': image_id,
        'results': results,
    })


@authorize_user
@authorize_admin
def confirm_select(request, image_id):
    feature = Feature.objects.get(identity=settings.FEATURE_IDENTITY, image=image_id)
    query_feat = np.frombuffer(feature.data, dtype='float32')
    results = get_results(query_feat)
    result_list = [ObjectId(x.id) for x in results[:100]]
    result_list = np.random.permutation(result_list).tolist()
    anno_query = AnnoQuery(query_image_id = ObjectId(image_id), target_image_ids = result_list)
    anno_query.save()
    return HttpResponseRedirect(reverse('annotator:select'))


def login(request, error=None, info=None):
    render_dict = {
        'login_form': LoginForm(),
        'register_form': RegisterForm(),
    }
    if error == '0':
        render_dict['error_message'] = 'Please check your input format!'
    elif error == '1':
        render_dict['error_message'] = 'Username or password incorrect!'
    elif error == '2':
        render_dict['error_message'] = 'Password not consistent!'
    elif error == '3':
        render_dict['error_message'] = 'Username already exist!'
    if info == '8':
        render_dict['info_message'] = 'Register success! Please login.'
    return render(request, 'annotator/login.html', render_dict)


def logout(request):
    try:
        del request.session['anno_user_id']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('annotator:login'))


def login_submit(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST supported')
    login_form = LoginForm(request.POST)
    if not login_form.is_valid():
        return HttpResponseRedirect(reverse('annotator:login_error', kwargs={
            'error': '0'
        }))
    try:
        data = login_form.cleaned_data
        user = AnnoUser.objects.get(user_name=data['user_name'])
        if not user.validate_password(data['password']):
            raise AnnoUser.DoesNotExist
        request.session['anno_user_id'] = str(user.id)
        # Redirect to select page if the user is admin
        if user.user_name == 'admin':
            return HttpResponseRedirect(reverse('annotator:select'))
        return HttpResponseRedirect(reverse('annotator:annotate'))
    except AnnoUser.DoesNotExist:
        return HttpResponseRedirect(reverse('annotator:login_error', kwargs={
            'error': '1'
        }))


def register(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST supported')
    register_form = RegisterForm(request.POST)
    if not register_form.is_valid():
        return HttpResponseRedirect(reverse('annotator:login_error', kwargs={
            'error': '0'
        }))
    data = register_form.cleaned_data
    if data['password'] != data['password_cfm']:
        return HttpResponseRedirect(reverse('annotator:login_error', kwargs={
            'error': '2'
        }))
    try:
        AnnoUser.objects.get(user_name=data['user_name'])
        return HttpResponseRedirect(reverse('annotator:login_error', kwargs={
            'error': '3'
        }))
    except AnnoUser.DoesNotExist:
        anno_user = AnnoUser(user_name=data['user_name'])
        anno_user.set_password(data['password'])
        anno_user.save()
        return HttpResponseRedirect(reverse('annotator:login_info', kwargs={
            'info': '8'
        }))


@authorize_user
def annotate(request):
    anno_user_id = request.session.get('anno_user_id')
    anno_user = AnnoUser.objects.get(id=anno_user_id)

    if anno_user.completed:
        return render(request, 'annotator/completed.html')

    render_dict = {
        'user_name': anno_user.user_name,
        'label_index': anno_user.label_index+1,
        'label_count': len(anno_user.annotation_list),
        'annotation_id': anno_user.current_annotation_id,
        'query_id': anno_user.current_query_id,
        'annotation_list': anno_user.current_annotation,
        'submit_form': AnnotateForm(),
    }
    return render(request, 'annotator/annotate.html', render_dict)

@authorize_user
def annotate_submit(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST supported')

    anno_user_id = request.session.get('anno_user_id')
    anno_user = AnnoUser.objects.get(id=anno_user_id)
    anno_form = AnnotateForm(request.POST)
    if not anno_form.is_valid():
        return HttpResponseBadRequest('Bad parameters!')
    annotation = AnnoAnnotation()
    annotation.user = anno_user_id
    annotation.query = request.POST['query_id']
    try:
        annotation.scores = json.loads(request.POST['scores'])
    except:
        return HttpResponseBadRequest('Bad score parameter!')
    # TODO: this may cause transaction inconsistent
    annotation.save()
    anno_user.label_index += 1
    anno_user.save()
    return HttpResponseRedirect(reverse('annotator:annotate'))