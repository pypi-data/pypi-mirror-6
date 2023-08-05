# -*- coding: utf-8 -*-

from PIL import Image
from os import path, sep, makedirs
from pycicu.schemas import receiveUpload
from pycicu.widget import pyCreateResourceRegistry

from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.response import Response
import deform

from StringIO import StringIO
import json
import os
import uuid

from pycicu.models import (DBSession, UploadedFile)

class ImageViews(object):
    
    def __init__(self, request):
        self.request = request
        settings = request.registry.settings
        self.USERFILES = settings['pycicu.userfiles']
        self.IMAGES_URL = settings['pycicu.images_url']
    
    def store_file(self, file_object, file_name):
        f_location = os.path.join(self.USERFILES, file_name)
        output_file = open(f_location, 'wb')
        file_object.seek(0)
        while True:
            data = file_object.read(2<<16)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        return f_location
    
    @view_config(route_name='pycicu-upload', request_method='POST')
    def upload(self):
        try:
            post = self.request.POST
            formatt = post.get('file').filename.rsplit('.', 1)[1]
            # ``input_file`` contains the actual file data which needs to be stored somewhere.
            input_file = post.get('file').file
            filename = '%s.%s' % (uuid.uuid4(), formatt)
            
            path = self.store_file(input_file, filename)
            rel_path = self.IMAGES_URL+'/'+filename
    
            image = UploadedFile()
            image.file = path
            DBSession.add(image)
            DBSession.flush()
    
            img = Image.open(path, mode='r')
            # get the image's width and height in pixels
            width, height = img.size
            data = {
                'path': rel_path,
                'id' : str(image.uid),
                'width' : width,
                'height' : height,
            }
            return Response(json.dumps(data))
        except Exception as e:
            return Response( json.dumps({'errors': str(e)}) )
    
    
    @view_config(route_name='pycicu-upload', renderer='pycicu:templates/teste.pt')#, request_method='POST')
    def teste_upload(self):
        schema = receiveUpload(request=self.request,)\
                               .bind(request=self.request,
                                     upload=self.request)
        form = deform.Form(schema, resource_registry=pyCreateResourceRegistry())
        if self.request.method == 'POST':
            post = self.request.POST
            
            formatt = post.get('file').filename.rsplit('.', 1)[1]
            # ``input_file`` contains the actual file data which needs to be stored somewhere.
            input_file = post.get('file').file
            filename = '%s.%s' % (uuid.uuid4(), formatt)
            
            path = self.store_file(input_file, filename)
            rel_path = self.IMAGES_URL+'/'+filename

            image = UploadedFile()
            image.file = path
            DBSession.add(image)
            DBSession.flush()

            img = Image.open(path, mode='r')
            # get the image's width and height in pixels
            width, height = img.size
            data = {
                'path': rel_path,
                'id' : str(image.uid),
                'width' : width,
                'height' : height,
            }
            return Response(json.dumps(data))
        
        else:
            appstruct = {}#record.to_appstruct()
            ret = {'form' : form.render(appstruct=appstruct), 
                   'requirements' : form.get_widget_resources(),}
            return ret
            
    @view_config(route_name='pycicu-crop', renderer='pycicu:templates/teste.pt')
    def crop(self):
        original_id = self.request.POST.get('id', None)
        original_file = DBSession.query(UploadedFile).get(original_id)
        original_img = Image.open( original_file.file, mode='r' )
        
        #gets the coordinates of the area that will be cropped
        box = self.request.POST.get('cropping', None)
        values = [int(float(x)) for x in box.split(',')]
        
        #do the cropping
        width = abs(values[2] - values[0])
        height = abs(values[3] - values[1])
        if width and height and (width <= original_img.size[0] and height <= original_img.size[1]):
            croppedImage = original_img.crop(values).resize((width, height), Image.ANTIALIAS)
        else:
            raise Exception( str(width)+' '+str(height) )
        
        
        new_file = UploadedFile()
        new_file.uid = uuid.uuid4()
        new_file.original_id = original_id
        DBSession.add(new_file)
        DBSession.flush()
        
        
        pathToFile = self.USERFILES
        formatt = original_file.file.rsplit('.')[-1]
        filename = str(new_file.uid)+'.'+formatt
        if not path.exists(pathToFile):
            makedirs(pathToFile)
        pathToFile = path.join(pathToFile, filename)
        croppedImage.save(pathToFile)


        new_file.file = pathToFile
        DBSession.merge(new_file)
        DBSession.flush()

        data = {
            'path': str(self.IMAGES_URL+'/'+filename),
            'id' : str(new_file.uid),
        }
        return Response(json.dumps(data))

