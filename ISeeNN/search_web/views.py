from django.shortcuts import render

from django.http import HttpResponse, HttpResponseGone, HttpResponseServerError, HttpResponseRedirect
from django.http import Http404
from django.conf import settings
from django.urls import reverse
import urllib.request, urllib.error
import time

# Create your views here.

from .search_engine import Index, push_index_item, exec_query, QueryType
import numpy as np
import sys

from .feature_extractor import ResizeExtractor, NoResizeExtractor, NormalizerFactory
from .models import Feature, DBImage, ImageServer, ImageUploadForm, UserUploadImage

def load_index(identity):
    print("loading index...")
    print("This may take a while.")
    index = Index()
    time_s = time.time()
    for db in settings.DATASETS:
        print("loading dataset %s" % db)
        loaded = 0
        images = DBImage.objects(source=db).only('id').all()
        image_ids = [x.id for x in images]
        time_m = time.time()
        count = len(image_ids)
        print("converted %d images in %.2fs" % (count, time_m - time_s))
        segment_size = 500000
        if count > segment_size:
            start_id = 0
            image_id_sets = []
            while start_id + segment_size < count:
                image_id_sets.append(image_ids[start_id:start_id + segment_size])
                start_id += segment_size
            if start_id < count:
                image_id_sets.append(image_ids[start_id:])
        else:
            image_id_sets = [image_ids]
        for image_id_clips in image_id_sets:
            for feature in Feature.objects(image__in=image_id_clips, identity=settings.FEATURE_IDENTITY).only('data').all():
                if loaded % 10000 == 0:
                    print('%d / %d' % (loaded, count))
                vec = np.frombuffer(feature.data, dtype='float32')
                push_index_item(index, str(feature.image), vec.tolist())
                loaded += 1
    time_e = time.time()
    print("loaded %d index items in %.2fs." % (index.size, time_e - time_s))
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
    def query(feat):
        results = exec_query(SearchEngine.index, feat.tolist(), QueryType.Linear, settings.MAX_RETURN_ITEM)
        return results

    @staticmethod
    def query_re_rank(feat):
        results = exec_query(SearchEngine.index, feat.tolist(), QueryType.LRS, settings.MAX_RETURN_ITEM)
        return results

    @staticmethod
    def extract(image_path):
        feat = SearchEngine.extractor.extract(image_path)
        feat = SearchEngine.normalizer.normalize(feat)
        return feat


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


def result(request, id, from_db=None, re_rank=None):
    try:
        if from_db == 'from_db':
            feature_db_image = Feature.objects.get(image=id, identity=settings.FEATURE_IDENTITY)
            feat_query = np.frombuffer(feature_db_image.data, dtype='float32')
        else:
            user_upload_image = UserUploadImage.objects.get(id=id)
            feat_query = np.frombuffer(user_upload_image.feature, dtype='float32')
        start_time = time.time()
        if re_rank == 're_rank':
            search_results = SearchEngine.query_re_rank(feat=feat_query)
        else:
            search_results = SearchEngine.query(feat=feat_query)
        end_time = time.time()
        results = []
        for item in search_results:
            (w, h) = get_image_meta(item.id)
            results.append(ResultMeta(item.id, item.score, w, h))
        return render(request, 'search_web/result.html', {
            'query_image': id,
            'time': '%.2f' % (end_time - start_time),
            'results': results,
            'from_db': from_db,
            're_rank': re_rank,
        })
    except (UserUploadImage.DoesNotExist, Feature.DoesNotExist):
        raise Http404("Page Not Found")


def handle_uploaded_image(request):
    image_file = request.FILES['image_file']
    user_upload_image = UserUploadImage()
    user_upload_image.data.put(image_file)
    feat_query = SearchEngine.extract(user_upload_image.data.get())
    user_upload_image.feature = feat_query.tobytes()
    user_upload_image.identity = settings.FEATURE_IDENTITY
    user_upload_image.save()
    return HttpResponseRedirect(reverse('search_web:result', kwargs={'id': str(user_upload_image.pk)}))


def upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_uploaded_image(request)
        else:
            print("Not valid")
            return HttpResponseRedirect(reverse('search_web:index'))
    return HttpResponseRedirect(reverse('search_web:index'))


def detail(request, image_id, user_upload_id, from_db=None):
    try:
        db_image = DBImage.objects.get(id=image_id)
        if from_db is None:
            user_upload_image = UserUploadImage.objects.get(id=user_upload_id)
            if user_upload_image.feature is None or user_upload_image.identity != settings.FEATURE_IDENTITY:
                feat_user_image = SearchEngine.extract(user_upload_image.data.get())
            else:
                feat_user_image = np.frombuffer(user_upload_image.feature, dtype='float32')
        else:
            feature_user_image = Feature.objects.get(image=user_upload_id, identity=settings.FEATURE_IDENTITY)
            feat_user_image = np.frombuffer(feature_user_image.data, dtype='float32')
        feature_db_image = Feature.objects.get(image=image_id, identity=settings.FEATURE_IDENTITY)
        feat_db_image = np.frombuffer(feature_db_image.data, dtype='float32')
        similarity = np.inner(feat_db_image, feat_user_image)
        return render(request, 'search_web/detail.html', {
            'similarity': '%.4f' % similarity,
            'user_upload_image_id': user_upload_id,
            'db_image': db_image,
            'from_db': from_db
        })
    except (DBImage.DoesNotExist, UserUploadImage.DoesNotExist):
        raise Http404
    except Feature.DoesNotExist:
        return HttpResponseServerError("Feature does not exist")

