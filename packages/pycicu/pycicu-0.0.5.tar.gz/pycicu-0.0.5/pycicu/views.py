# -*- coding: utf-8 -*-

from PIL import Image
from os import path, sep, makedirs
from pycicu import IMAGE_CROPPED_UPLOAD_TO
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


from familias import USERFILES

class ImageViews(object):
    
    def __init__(self, request):
        self.request = request
    
    valid_chars = set([i for i in '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'])

    def safe_filename(self, fn):
        return ''.join(c for c in fn if c in self.valid_chars)
    
    def store_file(self, file_object, file_name):
        f_location = os.path.join(USERFILES, file_name)
        output_file = open(f_location, 'wb')
        file_object.seek(0)
        while True:
            data = file_object.read(2<<16)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        return f_location
        
    def process_file(self, filedict):
        f = filedict['fp']
        fname = filedict['filename']
        file_location = self.store_file(f, fname)
        return file_location
    
    def merge_record_with_form(self, record, post):
        for key,value in post:
            if hasattr(record, key):
                setattr(record, key, value)
        return record
    
    @view_config(route_name='pycicu-upload', renderer='pycicu:templates/teste.pt')#, request_method='POST')
    def upload(self):
        schema = receiveUpload(request=self.request,)\
                               .bind(request=self.request,
                                     upload=self.request)
        form = deform.Form(schema, resource_registry=pyCreateResourceRegistry())
        if self.request.method == 'POST':
            post = self.request.POST
            
            format = post.get('file').filename.rsplit('.', 1)[1]
            # ``input_file`` contains the actual file data which needs to be stored somewhere.
            input_file = post.get('file').file
            filename = '%s.%s' % (uuid.uuid4(), format)
            
            path = self.store_file(input_file, filename)
            

            img = UploadedFile()
            img.file = filename
            DBSession.merge(img)
            DBSession.flush()

            img = Image.open(path, mode='r')
            # get the image's width and height in pixels
            width, height = img.size
            data = {
                'path': path,
                'id' : img.uid,
                'width' : width,
                'height' : height,
            }
            return Response(json.dumps(data))
        
        else:
            appstruct = {}#record.to_appstruct()
            ret = {'form' : form.render(appstruct=appstruct), 
                   'requirements' : form.get_widget_resources(),}
            
            
            #raise Exception()
            '''form = UploadedFileForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                uploaded_file = form.save()
                # pick an image file you have in the working directory
                # (or give full path name)
                img = Image.open(uploaded_file.file.path, mode='r')
                # get the image's width and height in pixels
                width, height = img.size
                data = {
                    'path': uploaded_file.file.url,
                    'id' : uploaded_file.id,
                    'width' : width,
                    'height' : height,
                }
                return HttpResponse(json.dumps(data))
            else:
                return HttpResponseBadRequest(json.dumps({'errors': form.errors}))
        
            f = StringIO()
            pdf = pisa.CreatePDF(result, f)
            response = Response(body=f.getvalue(), content_type="application/pdf",
                    content_disposition='attachment; filename="NovaPesquisa.pdf"')'''
            return ret#Response(body='upload')
    
    @view_config(route_name='pycicu-crop')
    def crop(self):
        '''try:
            if request.method == 'POST':
                box = request.POST.get('cropping', None)
                imageId = request.POST.get('id', None)
                uploaded_file = UploadedFile.objects.get(id=imageId)
                img = Image.open( uploaded_file.file.path, mode='r' )
                values = [int(x) for x in box.split(',')]
    
                width = abs(values[2] - values[0])
                height = abs(values[3] - values[1])
                if width and height and (width != img.size[0] or height != img.size[1]):
                    croppedImage = img.crop(values).resize((width,height),Image.ANTIALIAS)
    
                else:
                    raise
    
                pathToFile = path.join(settings.MEDIA_ROOT,IMAGE_CROPPED_UPLOAD_TO)
                if not path.exists(pathToFile):
                    makedirs(pathToFile)
                pathToFile = path.join(pathToFile,uploaded_file.file.path.split(sep)[-1])
                croppedImage.save(pathToFile)
    
                new_file = UploadedFile()
                f = open(pathToFile, mode='rb')
                new_file.file.save(uploaded_file.file.name, File(f))
                f.close()
    
                data = {
                    'path': new_file.file.url,
                    'id' : new_file.id,
                }
    
                return HttpResponse(json.dumps(data))
    
        except Exception:
            return HttpResponseBadRequest(json.dumps({'errors': 'illegal request'}))'''
        return Response(body='crop')

