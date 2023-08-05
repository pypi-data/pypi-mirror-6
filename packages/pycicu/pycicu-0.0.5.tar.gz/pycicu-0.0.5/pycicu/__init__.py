# -*- coding: utf-8 -*-

from sqlalchemy import engine_from_config

from .models import ( DBSession, Base )

from .widget import (CropedPhotoUploaderInput, deferred_croped_picture, 
                     pyCreateResourceRegistry)


UPLOADER_DELETE_AFTER = 3600
IMAGE_CROPPED_UPLOAD_TO = '/tmp'

def routes(config):
    config.add_static_view('static', 'pycicu:static', cache_max_age=0)
    
    config.add_route('pycicu-crop', '/ajax-upload/crop/')
    config.add_route('pycicu-upload', '/ajax-upload/')

def includeme(config):
    config.include(routes, route_prefix='/pycicu/')
    config.scan()
    
    settings = config.registry.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    
    
    global UPLOADER_DELETE_AFTER
    global IMAGE_CROPPED_UPLOAD_TO
    #raise Exception( settings )
    
    UPLOADER_DELETE_AFTER = settings['pycicu.cache_duration'] if 'pycicu.cache_duration' in settings else 3600
    IMAGE_CROPPED_UPLOAD_TO = settings['pycicu.userfiles']
    
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    

