# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseGone, HttpResponseBadRequest, HttpResponseServerError
from django.http import Http404
from django.conf import settings

# Create your views here.

from .models import DBImage, ImageServer


def get_image(request, id):
    try:
        db_image = DBImage.objects.get(id=id)
        try:
            server = ImageServer.objects.get(id=db_image.server)
            if server.server_name != settings.SERVER_NAME:
                return HttpResponseBadRequest("Image Not On This Server")
        except ImageServer.DoesNotExist:
            return HttpResponseServerError("Image Server Does Not Exist!")
        image_data = open(db_image.path, 'rb').read()
        mime_type = db_image.mime_type
        return HttpResponse(image_data, content_type=mime_type)
    except DBImage.DoesNotExist:
        raise Http404("Image Not Found")
    except IOError:
        return HttpResponseGone("Image Moved")


def get_thumbnail(request, id):
    try:
        db_image = DBImage.objects.get(id=id)
        thumbnail = db_image.get_thumbnail()
        image_data = thumbnail.file.read()
        mime_type = thumbnail.mime_type
        return HttpResponse(image_data, content_type=mime_type)
    except DBImage.DoesNotExist:
        raise Http404("Image Not Found")
    except IOError:
        return HttpResponseGone("Image Moved")

