import sys
import os
from PIL import Image

project_root = '../ISeeNN'
sys.path.append('../')
sys.path.append(os.path.join(project_root, 'search_web'))
sys.path.append(os.path.join(project_root, 'ISeeNN'))
import personal_settings as ps

from feature_extractor import ResizeExtractor, RootNormalizer
from ISeeNN.image_server.models import DBImage, DBImageThumbnail, ImageServer
from models import Feature, AestheticInfo

import mongoengine

_MONGODB_USER = ps._MONGODB_USER
_MONGODB_PASSWD = ps._MONGODB_PASSWD
_MONGODB_HOST = ps._MONGODB_HOST
_MONGODB_NAME = ps._MONGODB_NAME
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)

extensions = {".jpg"}


dir_name = '' # the directory you want to index
AVA_file = 'AVA.txt'
tags_file = 'tags.txt'

ext = ResizeExtractor('VGG16P5', (224,224))
server_id = ImageServer.objects.get(server_name='Amax').pk
norm = RootNormalizer()

def parse_tag_line(line):
    return (line[:line.find(' ')], line[line.find(' ')+1:-1])

tags = {}
with open(tags_file, 'r') as f:
    for line in f:
        (tag_id, tag_name) = parse_tag_line(line)
        tags[tag_id] = tag_name

def parse_ava_line(line): # '1 953619 0 1 5 17 38 36 15 6 5 1 1 22 1396'
    elements = line.split()
    file_id = elements[1]
    scores = 0.0
    nums = 0
    for x in range(1,11):
        scores += float(elements[x+1])*x
        nums += int(elements[x+1])
    score = scores / nums
    tag = []
    for x in range(12,14):
        if elements[x] != '0':
            tag.append(tags[elements[x]])
    return (file_id, score, tag)


with open(AVA_file, 'r') as f:
    for line in f:
        print(parse_ava_line(line))
        (file_id, score, tag) = parse_ava_line(line)
        img_filename = os.path.join(dir_name, file_id+'.jpg')
        if not os.path.isfile(img_filename):
            continue
        file_name, file_extension = os.path.splitext(img_filename)
        print(img_filename)
        try:
            db_image = DBImage.objects.get(path=img_filename)
            image_id = db_image.pk
        except DBImage.DoesNotExist:
            im = Image.open(img_filename)
            # if im.format != 'JPEG':
            #     continue
            db_image = DBImage(
                server=server_id,
                path=img_filename,
                width=im.width,
                height=im.height,
                mime_type='image/' + im.format.lower()
            )
            db_image.save()
            image_id = db_image.pk
        finally:
            try:
                feature = Feature.objects.get(image=image_id, identity='VGG16P5_resize')
            except Feature.DoesNotExist:
                try:
                    feat = ext.extract(img_filename)
                    feat = norm.normalize(feat)
                    Feature.objects(image=image_id, identity='VGG16P5_resize').update_one(
                        set__image=image_id,
                        set__dimension=feat.size,
                        set__model='VGG16P5',
                        set__data=feat.tobytes(),
                        upsert=True
                    )
                except:
                    pass
            try:
                aestheticInfo = AestheticInfo.objects.get(image=image_id)
            except AestheticInfo.DoesNotExist:
                try:
                    AestheticInfo.objects(image=image_id).update_one(
                        set__image=image_id,
                        set__score=score,
                        set__tags=tag,
                        upsert=True
                    )
                except:
                    pass
