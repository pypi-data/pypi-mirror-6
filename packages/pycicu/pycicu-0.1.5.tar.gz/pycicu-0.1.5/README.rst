#. TODO: Adjust this README to the new project. Right now it demands a lot of packages, in the future we intend to reduce them to a minimum.

py-clean-image-crop-uploader (pyCICU)
================================
.. image:: https://d2weczhvl823v0.cloudfront.net/asaglimbeni/django-datetime-widget/trend.png
    :target: https://bitdeli.com/free
.. image:: https://pypip.in/v/pycicu/badge.png
    :target: https://crate.io/packages/pycicu
.. image:: https://pypip.in/d/pycicu/badge.png
    :target: https://crate.io/packages/pycicu
    
``pycicu`` is a tool to upload an image via Ajax and crop it using `Jcrop
<https://github.com/tapmodo/Jcrop>`_. It provides a simple workflow: first one, using modal,
(by `twitter bootstrap <http://twitter.github.com/bootstrap/javascript.html#modals>`_) the image can be uploaded and cropped.
Second one, you can see the image cropping preview in the form and finally submit the result.

``pycicu`` is perfect when you have to upload images and it's necessary to have a specific portion of image. 
It'll be easy to configure and to use.
You can use different configurations, with fixed aspect ratio or minimal image size.

It works with jQuery = 1.8.3 and twitter bootstrap.

Screenshot:

#. Modal window with upload button:

.. image:: http://asaglimbeni.github.com/clean-image-crop-uploader/images/screenshot1.jpg

#. Modal window with crop area:

.. image:: http://asaglimbeni.github.com/clean-image-crop-uploader/images/screenshot2.jpg

#. Form with preview

.. image:: http://asaglimbeni.github.com/clean-image-crop-uploader/images/screenshot3.jpg

Installation
------------

#. Install using pip. For example::

    pip install pycicu


Dependencies
------------
* jQuery = 1.8.3
* Twitter-Bootstrap

* Pillow >= 1.5
* deform >= 2.0a2
* colander >= 1.0b1
* pyramid_chameleon >= 0.1
* SQLAlchemy >= 0.8.3

Configuration
-------------
#. Add into url.py ::

    (r'^ajax-upload/', include('startproject.cicu.urls'))

#. Create your model-form and set  CicuUploaderInput widget to your imageField  ::

    from cicu.widgets import CicuUploaderInput

    class yourCrop(forms.ModelForm):
        class Meta:
            model = yourModel
            cicuOptions = {
                'ratioWidth': '600',       #fix-width ratio, default 0
                'ratioHeight':'400',       #fix-height ratio , default 0
                'sizeWarning': 'False',    #if True the crop selection have to respect minimal ratio size defined above. Default 'False'
            }
            widgets = {
                'image': CicuUploaderInput(options=cicuOptions)
            }

#. Download `twitter bootstrap <http://twitter.github.com/bootstrap/>`_  to your static file folder.

#. Add in your form template links to jquery, bootstrap, form.media::

    <head>
    ....
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
        <link href="{{ STATIC_URL }}css/bootstrap.css" rel="stylesheet" type="text/css"/>
        <script src="{{ STATIC_URL }}js/bootstrap.js"></script>
        {{ form.media }}

    ....
    </head>


Run the example
---------------

To run the example inside this package follow these commands::

    > cd ./example/
    > python manage.py syncdb
    > python manage.py migrate # only if you use South!!!
    > python manage.py collectstatic
    > python manage.py runserver domain:8000

Go to examples :

#. Free crop : <http://domain:8000/cicu-freecrop/>

#. Fixed aspect ratio: <http://domain:8000/cicu-fixedratio/>

#. Fixed aspect ratio with minimal size: <http://domain:8000/cicu-warningsize/>





