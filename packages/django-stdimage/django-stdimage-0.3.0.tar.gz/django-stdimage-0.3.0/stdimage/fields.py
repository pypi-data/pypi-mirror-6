# -*- coding: utf-8 -*-
import os
import shutil
from warnings import warn

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import signals
from django.db.models.fields.files import ImageField, ImageFileDescriptor
from forms import StdImageFormField
from widgets import DelAdminFileWidget


class ThumbnailField(object):
    """Instances of this class will be used to access data of the
    generated thumbnails

    """

    def __init__(self, name):
        warn('%(class)s has been deprecated in favor of VariationsField()', DeprecationWarning)
        self.name = name
        self.storage = FileSystemStorage()

    def path(self):
        return self.storage.path(self.name)

    def url(self):
        return self.storage.url(self.name)

    def size(self):
        return self.storage.size(self.name)


class VariationField(object):
    """Instances of this class will be used to access data of the generated variations."""

    def __init__(self, name):
        """

        :param name: str
        """
        self.name = name
        self.storage = FileSystemStorage()

    @property
    def path(self):
        """Return the abs. path of the image file."""
        return self.storage.path(self.name)

    @property
    def url(self):
        """Return the url of the image file."""
        return self.storage.url(self.name)

    @property
    def size(self):
        """Return the size of the image file, reported by os.stat()."""
        return self.storage.size(self.name)


class StdImageFileDescriptor(ImageFileDescriptor):
    """
    The thumbnail property of the field should be accessible in instance cases

    """

    def __set__(self, instance, value):
        super(StdImageFileDescriptor, self).__set__(instance, value)
        self.field.set_variations(instance)


class StdImageField(ImageField):

    """
    Django field that behaves as ImageField, with some extra features like:
        - Auto resizing
        - Allow image deletion

    :param variations: size variations of the image
    """
    descriptor_class = StdImageFileDescriptor

    def __init__(self, verbose_name=None, name=None, variations={}, *args, **kwargs):
        """
        Standardized ImageField for Django
        Usage: StdImageField(upload_to='PATH', variations={'thumbnail': (width, height, boolean, algorithm)})
        :param variations: size variations of the image
        :rtype variations: StdImageField
        """
        size = kwargs.pop('size', None)
        thumbnail_size = kwargs.pop('thumbnail_size', None)
        if size or thumbnail_size:
            warn('Size and thumbnail_size keyword arguments are deprecated in favor of variations.', DeprecationWarning)

        param_size = ('width', 'height', 'crop', 'resample')

        if not 'size' in variations and size:
            variations['size'] = size
        if not 'thumbnail' in variations and thumbnail_size:
            variations['thumbnail'] = thumbnail_size

        self.variations = []

        for key, attr in variations.iteritems():
            if attr and isinstance(attr, (tuple, list)):
                variation = dict(map(None, param_size, attr))
                variation['name'] = key
                setattr(self, key, variation)
                self.variations.append(variation)
            else:
                setattr(self, key, None)

        super(StdImageField, self).__init__(verbose_name, name, *args, **kwargs)

    def _get_thumbnail_filename(this, filename):
        """ Deprecated in favor of _get_variation_filename(variation, filename)
        """
        warn("This getter is deprecated in favor of _get_variation_filename(variation, filename).", DeprecationWarning)
        splitted_filename = list(os.path.splitext(filename))
        splitted_filename.insert(1, '.thumbnail')
        return ''.join(splitted_filename)

    @staticmethod
    def _get_variation_filename(variation, filename):
        """
        Returns the filename of the picture's right size asscociated to sthe standart image filename

        :rtype : str
        :param variation: variation
        :param filename: filename
        :return: full file path
        """
        splitted_filename = list(os.path.splitext(filename))
        splitted_filename.insert(1, '.%s' % variation['name'])
        return ''.join(splitted_filename)

    @staticmethod
    def _resize_image(filename, size):
        """
        Resizes the image to specified width, height and optional crop and resample.

        :param filename: str
        :param size: dict
        """
        width, height = 0, 1

        try:
            import Image, ImageOps
        except ImportError:
            from PIL import Image, ImageOps

        if not size['resample']:
            resample = Image.ANTIALIAS

        img = Image.open(filename)
        if (img.size[width] > size['width'] or
                    img.size[height] > size['height']):

            #If the image is big resize it with the cheapest resize algorithm
            factor = 1
            while (img.size[0] / factor > 2 * size['width'] and
                                   img.size[1] * 2 / factor > 2 * size['height']):
                factor *= 2
            if factor > 1:
                img.thumbnail((int(img.size[0] / factor),
                               int(img.size[1] / factor)), resample=resample)

            if size['crop']:
                img = ImageOps.fit(img, (size['width'], size['height']), method=resample)
            else:
                img.thumbnail((size['width'], size['height']), resample=resample)

            try:
                img.save(filename, optimize=1)
            except IOError:
                img.save(filename)

    def _rename_resize_image(self, instance=None, **kwargs):
        """Renames the image, and calls methods to resize and create the variations."""
        if getattr(instance, self.name):
            filename = getattr(instance, self.name).path
            ext = os.path.splitext(filename)[1].lower().replace('jpg', 'jpeg')
            dst = self.generate_filename(instance, '%s_%s%s' % (self.name,
                                                                instance._get_pk_val(), ext))
            dst_fullpath = os.path.join(settings.MEDIA_ROOT, dst)
            if os.path.abspath(filename) != os.path.abspath(dst_fullpath):
                os.rename(filename, dst_fullpath)
                for variation in self.variations:
                    variation_filename = self._get_variation_filename(variation, dst_fullpath)
                    shutil.copyfile(dst_fullpath, variation_filename)
                    self._resize_image(variation_filename, variation)
                setattr(instance, self.attname, dst)
                instance.save()

    def _set_thumbnail(self, instance=None, **kwargs):
        """
        Creates a "thumbnail" object as attribute of the ImageField instance
        Thumbnail attribute will be of the same class of original image, so
        "path", "url"... properties can be used
        """
        warn('This setter is deprecated in favor of _set_variations.', DeprecationWarning)
        if getattr(instance, self.name):
            filename = self.generate_filename(instance,
                                              os.path.basename(getattr(instance, self.name).path))
            variation = getattr(self, 'thumbnail')
            thumbnail_filename = self._get_variation_filename(variation, filename)
            thumbnail_field = VariationField(thumbnail_filename)
            setattr(getattr(instance, self.name), 'thumbnail', thumbnail_field)

    def set_variations(self, instance=None, **kwargs):
        """
        Creates a "variation" object as attribute of the ImageField instance.
        Variation attribute will be of the same class as the original image, so
        "path", "url"... properties can be used

        :param instance: FileField
        """
        if getattr(instance, self.name):
            filename = self.generate_filename(instance,
                                              os.path.basename(getattr(instance, self.name).path))
            for variation in self.variations:
                if variation['name'] != 'size':
                    variation_filename = self._get_variation_filename(variation, filename)
                    variation_field = VariationField(variation_filename)
                    setattr(getattr(instance, self.name), variation['name'], variation_field)

    def formfield(self, **kwargs):
        """Specify form field and widget to be used on the forms"""
        kwargs['widget'] = DelAdminFileWidget
        kwargs['form_class'] = StdImageFormField
        return super(StdImageField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        """
        Overwrite save_form_data to delete images if "delete" checkbox is selected

        :param instance: Form
        """
        if data == '__deleted__':
            filename = getattr(instance, self.name).path
            if os.path.exists(filename):
                os.remove(filename)
            for variation in self.variations:
                variation_filename = self._get_variation_filename(variation, filename)
                if os.path.exists(variation_filename):
                    os.remove(variation_filename)
                    setattr(instance, self.name, None)
        else:
            super(StdImageField, self).save_form_data(instance, data)

    def get_db_prep_save(self, value, connection=None):
        """Overwrite get_db_prep_save to allow saving nothing to the database if image has been deleted"""
        if value:
            return super(StdImageField, self).get_db_prep_save(value, connection=connection)
        else:
            return u''

    def contribute_to_class(self, cls, name):
        """Call methods for generating all operations on specified signals"""

        super(StdImageField, self).contribute_to_class(cls, name)
        signals.post_save.connect(self._rename_resize_image, sender=cls)
        signals.post_init.connect(self.set_variations, sender=cls)
