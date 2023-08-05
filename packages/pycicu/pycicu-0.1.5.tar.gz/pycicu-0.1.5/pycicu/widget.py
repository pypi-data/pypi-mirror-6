# -*- coding: utf-8 -*-

import csv
import json
import random

#from pycicu import settings
#from PIL import Image
from pycicu.models import UploadedFile

import deform
import colander
from deform.compat import (
    string_types,
    StringIO,
    string,
    url_quote,
    uppercase,
    )
from deform.i18n import _

from pyramid_deform import SessionFileUploadTempStore
from deform.interfaces import FileUploadTempStore 
tmpstore = FileUploadTempStore()


def pyCreateResourceRegistry(resourceRegistry=None):
    if resourceRegistry is None:
        pycicu_resource_registry = deform.widget.ResourceRegistry(use_defaults=True)
    else:
        pycicu_resource_registry = resourceRegistry
    pycicu_resource_registry.registry['pycicu_croped'] = { 
                     None: { 'js': ("pycicu:static/js/jquery.Jcrop.min.js",
                                    "pycicu:static/js/jquery.iframe-transport.js",
                                    "pycicu:static/js/pycicu-widget.js",),
                             'css': ("pycicu:static/css/jquery.Jcrop.min.css", 
                                     "pycicu:static/css/pycicu-widget.css"), 
                            }, }
    return pycicu_resource_registry


class CropedPhotoUploaderInput(deform.widget.Widget):
    template = "pycicu:templates/croped_photo_upload.pt"
    readonly_template = "pycicu:templates/croped_photo_upload.pt"

    template_with_initial = '%(input)s'
    
    requirements = ( ('pycicu_croped', None), )


    def random_id(self):
        return ''.join([random.choice(uppercase+string.digits) for i in range(10)])

    def __init__(self, tmpstore, request, **kw):
        deform.widget.Widget.__init__(self, **kw)
        options = kw['options'] if 'options' in kw else {}

        #jcrop configuration
        self.options = {
            'sizeWarning': options.get('sizeWarning', 'True'),
            'ratioWidth': options.get('ratioWidth', ''),
            'ratioHeight': options.get('ratioHeight', ''),
    
            'modalButtonLabel': options.get('modalButtonLabel', _('Upload image')),
            'changeButtonText': options.get('changeButtonText', _('Change Image')),
            'sizeAlertMessage': options.get('sizeAlertMessage', _('Warning: The area selected is too small.  Min size:')),
            'sizeErrorMessage': options.get('sizeErrorMessage', _("Image doesn't meet the minimum size requirements ")),
            'modalSaveCropMessage': options.get('modalSaveCropMessage', _('Set image')),
            'modalCloseCropMessage': options.get('modalCloseCropMessage', _('Close')),
            'uploadingMessage': options.get('uploadingMessage', _('Uploading your image')),
            'fileUploadLabel': options.get('fileUploadLabel', _('Select image from your computer')),
        }
        self.request = request


    def get_template_values(self, field, cstruct, kw):
        values = {'cstruct':cstruct, 'field':field}
        values.update(kw)
        values.pop('template', None)
        return values

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = {}
        if cstruct:
            uid = cstruct['uid']
            kw['uid'] = uid
            if not uid in self.tmpstore:
                self.tmpstore[uid] = cstruct

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        kw['options'] = self.options
        kw['request'] = self.request
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)


    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null

        upload = pstruct.get('upload')
        uid = pstruct.get('uid')

        if hasattr(upload, 'file'):
            # the upload control had a file selected
            data = dict()
            data['fp'] = upload.file
            filename = upload.filename
            # sanitize IE whole-path filenames
            filename = filename[filename.rfind('\\')+1:].strip()
            data['filename'] = filename
            data['mimetype'] = upload.type
            data['size']  = upload.length
            if uid is None:
                # no previous file exists
                while 1:
                    uid = self.random_id()
                    if self.tmpstore.get(uid) is None:
                        data['uid'] = uid
                        self.tmpstore[uid] = data
                        preview_url = self.tmpstore.preview_url(uid)
                        self.tmpstore[uid]['preview_url'] = preview_url
                        break
            else:
                # a previous file exists
                data['uid'] = uid
                self.tmpstore[uid] = data
                preview_url = self.tmpstore.preview_url(uid)
                self.tmpstore[uid]['preview_url'] = preview_url
        else:
            # the upload control had no file selected
            if uid is None:
                # no previous file exists
                return colander.null
            else:
                print uid
                # a previous file should exist
                data = self.tmpstore.get(uid)
                # but if it doesn't, don't blow up
                if data is None:
                    return colander.null

        return data

class TmpStore(SessionFileUploadTempStore):

    def __init__(self, request):
        self.tempdir = request.registry.settings.get('pyramid_deform.tempdir', '/tmp')
        self.request = request
        self.session = request.session
        self.tempstore = self.session.setdefault('tempstore', {})



@colander.deferred
def deferred_croped_picture(node, kw):
    request = kw.get('request')
    return CropedPhotoUploaderInput(TmpStore(request), request)


class pycicuException(Exception):
    pass


'''class CropUploaderInput(forms.ClearableFileInput):


    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        if value:
            filename = u'%s%s' % (settings.MEDIA_URL, value)
        else:
            filename = ''
        attrs.update({
            'class': attrs.get('class', '') + 'ajax-upload',
            'data-filename': filename, # This is so the javascript can get the actual value
            'data-required': self.is_required or '',
            'data-upload-url': reverse('ajax-upload'),
            'data-crop-url': reverse('pycicu-crop'),
            'type': 'file',
            'accept' : 'image/*',
        })
        output = super(pycicuUploaderInput, self).render(name, value, attrs)
        option = self.optionsInput % self.options
        autoDiscoverScript = "<script>$(function(){pycicuWidget.autoDiscover();});</script>"
        return mark_safe(output + option + autoDiscoverScript)

    def value_from_datadict(self, data, files, name):
        # If a file was uploaded or the clear checkbox was checked, use that.
        file = super(pycicuUploaderInput, self).value_from_datadict(data, files, name)
        if file is not None:  # super class may return a file object, False, or None
            return file  # Default behaviour
        elif name in data:  # This means a file id was specified in the POST field
            try:
                uploaded_file = UploadedFile.objects.get(id=data.get('image'))
                img = Image.open(uploaded_file.file.path, mode='r')
                width, height = img.size
                if (width < self.options[1] or height < self.options[2]) and self.options[0] == 'True':
                    raise Exception('Image don\'t have correct ratio %sx%s' % (self.options[1], self.options[2]))
                return uploaded_file.file
            except Exception, e:
                return None
        return None'''






