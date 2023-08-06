.. image:: https://travis-ci.org/codingjoe/django-stdimage.png
  :target: https://travis-ci.org/codingjoe/django-stdimage
.. image:: https://pypip.in/v/django-stdimage/badge.png
  :target: https://crate.io/packages/django-stdimage
.. image:: https://pypip.in/d/django-stdimage/badge.png
  :target: https://crate.io/packages/django-stdimage
.. image:: https://pypip.in/license/django-stdimage/badge.png
  :target: https://pypi.python.org/pypi/django-stdimage/

Django Standarized Image Field
==============================

Django Field that implement the following features:

* Django-Storages compatible (S3)
* Resize images to different sizes
* Access thumbnails on model level, no template tags required
* Preserves original image
* Restrict accepted image dimensions
* Allow image deletion
* Rename files to a standardized name (using a callable upload_to)

Installation
------------

Install latest PIL - there is really no reason to use this package without it

`easy_install django-stdimage`

or

`pip django-stdimage`

Put `'stdimage'` in the INSTALLED_APPS

Usage
-----

Import it in your project, and use in your models.

Example::

    from stdimage import StdImageField

    class MyClass(models.Model):
        # works as ImageField
        image1 = StdImageField(upload_to='path/to/img')

        # can be deleted through admin
        image2 = StdImageField(upload_to='path/to/img', blank=True)

        # creates a thumbnail resized to maximum size to fit a 100x75 area
        image3 = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 75)})

        # creates a thumbnail resized to 100x100 croping if necessary
        image4 = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 100, True})

        # creates a thumbnail resized to 100x100 croping if necessary and excepts only image greater than 1920x1080px
        image5 = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 100, True}, min_size(1920,1080))

        # all previous features in one declaration
        image_all = StdImageField(upload_to='path/to/img', blank=True,
                        variations={'large': (640, 480), 'thumbnail': (100, 100, True)})

For using generated thumbnail in templates use "myimagefield.thumbnail". Example::

    <a href="{{ object.myimage.url }}"><img alt="" src="{{ object.myimage.thumbnail.url }}"/></a>

About image names
-----------------

By default StdImageField stores images without modifying the file name. If you want to use more consistent file names you can use the build in upload functions.
Example::

    from stdimage import StdImageField, UPLOAD_TO_CLASS_NAME, UPLOAD_TO_CLASS_NAME_UUID, UPLOAD_TO_UUID
    from functools import partial

    class MyClass(models.Model)
        # Gets saved to MEDIA_ROOT/myclass/#FILENAME#.#EXT#
        image1 = StdImageField(upload_to=UPLOAD_TO_CLASS_NAME)

        # Gets saved to MEDIA_ROOT/myclass/pic.#EXT#
        image2 = StdImageField(upload_to=partial(UPLOAD_TO_CLASS_NAME, name='pic'))

        # Gets saved to MEDIA_ROOT/images/#UUID#.#EXT#
        image3 = StdImageField(upload_to=partial(UPLOAD_TO_UUID, path='images'))

        # Gets saved to MEDIA_ROOT/myclass/#UUID#.#EXT#
        image4 = StdImageField(upload_to=UPLOAD_TO_CLASS_NAME_UUID)

About image names
-----------------

You can restrict the upload dimension of images using `min_size` and `max_size`. Both arguments accept a (width, height) tuple. By default, the minimum resolution is set to the biggest variation.
CAUTION: The `max_size` should be used with caution. As storage isn't expensive, you shouldn't restrict upload dimensions. If you seek prevent users form overflowing your memory you should restrict the HTTP upload body size.

.. image:: https://d2weczhvl823v0.cloudfront.net/codingjoe/django-stdimage/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free
