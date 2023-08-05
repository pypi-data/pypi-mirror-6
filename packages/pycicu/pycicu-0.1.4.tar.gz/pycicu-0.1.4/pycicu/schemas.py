# -*- coding: utf-8 -*-

import colander
import deform

from .widget import deferred_croped_picture

class receiveUpload(colander.Schema):
    
    #def __init__(self, *args, **kwargs):
    #    if 'request' in kwargs and kwargs['request'].method == 'POST':
    #        request = kwargs['request']
    #            
    #    super(AnexosFotosSchema, self).__init__(*args, **kwargs)
        

    upload = colander.SchemaNode(
                    deform.FileData(),
                    title=u'Campo temporário para testes',
                    widget=deferred_croped_picture
                    )