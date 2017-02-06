from django.shortcuts import render

from django.http import HttpResponse, HttpResponseGone, HttpResponseServerError, HttpResponseRedirect
from django.http import Http404
from django.conf import settings
from django.urls import reverse
import urllib.request, urllib.error
import time

# Create your views here.

from .search_engine import Index, push_index_item, exec_query
import numpy as np
import sys

from .feature_extractor import ResizeExtractor, NoResizeExtractor, NormalizerFactory
from .models import Feature, DBImage, ImageServer, ImageUploadForm, UserUploadImage

def load_index(identity):
    print("loading index...")
    print("This may take a while.")
    index = Index()
    for feature in Feature.objects(identity=identity).all():
        vec = np.frombuffer(feature.data, dtype='float32')
        push_index_item(index, str(feature.image), vec.tolist())
    print("loaded %d index items." % (index.size))
    return index

def load_extractor():
    if settings.INPUT_TYPE == 'NO_RESIZE':
        return NoResizeExtractor(settings.FEATURE_MODEL)
    elif settings.INPUT_TYPE == 'RESIZE':
        return ResizeExtractor(settings.FEATURE_MODEL, settings.INPUT_SIZE)


class SearchEngine:
    index = load_index(settings.FEATURE_IDENTITY)
    extractor = load_extractor()
    normalizer = NormalizerFactory.get(settings.NORMALIZER_TYPE)

    @staticmethod
    def size():
        return SearchEngine.index.size

    @staticmethod
    def query(image_path):
        feat = SearchEngine.extractor.extract(image_path)
        feat = SearchEngine.normalizer.normalize(feat)
        results = exec_query(SearchEngine.index, feat[0].tolist())
        return results

def get_image(request, id):
    try:
        db_image = DBImage.objects.get(id=id)
        mime_type = db_image.mime_type
        try:
            server = ImageServer.objects.get(id=db_image.server)
            ip = server.server_ip
            port = request.META['SERVER_PORT']
            url_ext = reverse('image_server:get_image', args=(str(id) ,))
            remote_url = 'http://' + ip + ':' + str(port) + url_ext
            image_data = urllib.request.urlopen(remote_url).read()
            return HttpResponse(image_data, content_type=mime_type)
        except ImageServer.DoesNotExist:
            return HttpResponseServerError("Image Server Does Not Exist!")
    except DBImage.DoesNotExist:
        raise Http404("Image Not Found")
    except:
        return HttpResponseGone("Image Moved")

def get_thumbnail(request, id):
    try:
        db_image = DBImage.objects.get(id=id)
        mime_type = db_image.mime_type
        try:
            server = ImageServer.objects.get(id=db_image.server)
            ip = server.server_ip
            port = request.META['SERVER_PORT']
            url_ext = reverse('image_server:get_thumbnail', args=(str(id) ,))
            remote_url = 'http://' + ip + ':' + str(port) + url_ext
            image_data = urllib.request.urlopen(remote_url).read()
            return HttpResponse(image_data, content_type=mime_type)
        except ImageServer.DoesNotExist:
            return HttpResponseServerError("Image Server Does Not Exist!")
    except DBImage.DoesNotExist:
        raise Http404("Image Not Found")
    except:
        return HttpResponseGone("Image Moved")

def user_image(request, id, thumbnail=None):
    try:
        user_image = UserUploadImage.objects.get(id=id)
        mime_type = "image/" + user_image.data.format
        if thumbnail:
            return HttpResponse(user_image.data.thumbnail.read(), content_type=mime_type)
        else:
            return HttpResponse(user_image.data.read(), content_type=mime_type)
    except UserUploadImage.DoesNotExist:
        raise Http404("Image Not Found")

def index(request):
    return render(request, 'search_web/index.html')

def get_image_meta(id):
    dbimage = DBImage.objects.get(pk=id)
    return (dbimage.width, dbimage.height)

class ResultMeta:
    def __init__(self, id, score, width, height):
        self.id = id
        self.score = score
        self.width = width
        self.height = height


def handle_uploaded_image(request):
    image_file = request.FILES['image_file']
    user_upload_image = UserUploadImage()
    user_upload_image.data.put(image_file)
    user_upload_image.save()

    start_time = time.time()
    search_results = SearchEngine.query(user_upload_image.data.get())
    end_time = time.time()
    results = []
    for item in search_results:
        (w, h) = get_image_meta(item.id)
        results.append(ResultMeta(item.id, item.score, w, h))
    query_image = str(user_upload_image.pk)
    return render(request, 'search_web/result.html', {
        'query_image': query_image,
        'time': '%.2f' % (end_time - start_time),
        'results': results
    })

def upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_uploaded_image(request)
        else:
            print("Not valid")
            return HttpResponseRedirect(reverse('search_web:index'))
    return HttpResponseRedirect(reverse('search_web:index'))

# def result(request):
#     return render(request, 'search_web/result.html')