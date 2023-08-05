# -*- coding: utf-8 -*-

from .widget import (CropedPhotoUploaderInput, deferred_croped_picture, 
                     pyCreateResourceRegistry)

# Number of seconds to keep uploaded files. The clean_uploaded command will
# delete them after this has expired.
UPLOADER_DELETE_AFTER =  60 * 60
IMAGE_CROPPED_UPLOAD_TO = 'pycicu_cropped/'

def routes(config):
    config.add_static_view('static', 'pycicu:static', cache_max_age=0)
    
    config.add_route('pycicu-crop', '/ajax-upload/crop/')
    config.add_route('pycicu-upload', '/ajax-upload/')

def includeme(config):
    config.include(routes, route_prefix='/pycicu/')
    config.scan()
    

