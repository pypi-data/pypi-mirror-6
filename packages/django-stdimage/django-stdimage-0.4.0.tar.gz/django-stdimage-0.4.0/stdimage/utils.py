import os
import uuid


def upload_to(name, ext, path=''):
    return os.path.join(path, '%s.%s' % (name, ext)).lower()


def upload_to_uuid(instance, filename, path=''):
    ext = filename.rsplit('.', 1)[-1]
    return upload_to(uuid.uuid4(), ext, path)


def upload_to_class_name_dir(instance, filename, name=''):
    ext = filename.rsplit('.', 1)[-1]
    if name == '':
        name = filename.rsplit('/', 1)[-1]
    class_name = instance.__class__.__name__
    return upload_to(name, ext, class_name)


def upload_to_class_name_dir_uuid(instance, filename):
    return upload_to_class_name_dir(instance, filename, uuid.uuid4())