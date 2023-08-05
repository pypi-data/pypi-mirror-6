# -*- coding: utf-8 -*-

from datetime import datetime
import uuid

import pyramid

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    class_mapper
    )

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import types
from sqlalchemy.schema import Column
from sqlalchemy.orm import class_mapper
from StringIO import StringIO


from sqlalchemy import (
        Column,
        String,
        ForeignKey,
        DateTime,
        )

from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.orderinglist import ordering_list
from pyramid.security import Allow


class UUID(types.TypeDecorator):
    impl = types.LargeBinary

    def __init__(self, length=16):
        self.impl.length = length
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return value.bytes
        elif value and isinstance(value, basestring):
            return uuid.UUID(value).bytes
        elif value:
            raise ValueError('value %s is not a valid uuid.UUId' % value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return uuid.UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class UploadedFile(Base):
    __tablename__ = 'pycicu_uploaded_file'

    uid = Column(UUID, primary_key = True, default=uuid.uuid4())
    file = Column(String, nullable=True)
    original_id = Column(UUID, ForeignKey('pycicu_uploaded_file.uid'), nullable=True)
    creation_date = Column(DateTime, default=datetime.now())

    def __unicode__(self):
        return unicode(self.file)
    
    @property
    def url(self):
        filename = self.file.rsplit('/', 1)[-1]
        file_url = '/userfiles/pycicu/'+str(filename)
        return file_url
        
    
    '''def delete(self, *args, **kwargs):
        super(UploadedFile, self).delete(*args, **kwargs)
        if self.file:
            self.file.delete()'''


