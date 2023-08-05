# -*- coding: utf-8 -*-

from .widget import (CropedPhotoUploaderInput, deferred_croped_picture, 
                     pyCreateResourceRegistry)

from sqlalchemy import engine_from_config

from .models import (DBSession, Base)

def routes(config):
    config.add_static_view('static', 'pycicu:static', cache_max_age=0)
    
    config.add_route('pycicu-crop', '/ajax-upload/crop/')
    config.add_route('pycicu-upload', '/ajax-upload/')

def includeme(config):
    settings = config.registry.settings
    
    #global DBSession
    #global Base
    
    #if 'DBSession' not in settings:
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    #else:
    #    DBSession = settings['DBSession']
    #    Base = settings['Base']
    
    config.include(routes, route_prefix='/pycicu/')
    config.scan()
    

