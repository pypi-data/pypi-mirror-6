import os
from s4u.image.model import Image
from s4u.image.model import ImageScale


def configure(original_path, scale_path):
    """Configure the filesystem paths used to store image files.

    :param original_path: filesystem path used for full size images.
    :param scale_path: filesystem path used for scaled images.
    """
    Image.root_path = original_path
    ImageScale.root_path = scale_path


def includeme(config):
    """Configure s4u.image using a Pyramid :py:class:`Configurator
    <pyramid.config.Configurator>` object. This will take the filesystem
    paths from the application settings using the keys
    ``fs.images.original`` and ``fs.images.scaled``.
    """
    settings = config.registry.settings
    configure(settings['fs.images.original'],
              settings['fs.images.scaled'])
    for key in ['original', 'scaled']:
        base_url = settings.get('fs.images.%s.url' % key)
        if base_url:
            config.add_static_view(base_url,
                    settings['fs.images.%s' % key])
        else:
            config.add_static_view('image-%s' % key,
                    settings['fs.images.%s' % key],
                    cache_max_age=86400 * 31)


def initialise_filesystem():
    """Create required filesystem.

    This function requires that s4u.image is already configured.

    It is safe to call this function multiple times: it will notice if a
    directory already exists.
    """
    _create_directories(Image.root_path)
    _create_directories(ImageScale.root_path)


def _create_directories(root_path):
    if not os.path.isdir(root_path):
        raise RuntimeError('%s is not a valid image root path' % root_path)
    for top in range(16):
        top_path = os.path.join(root_path, '%x' % top)
        if not os.path.exists(top_path):
            os.mkdir(top_path)
        for sub in range(256):
            sub_path = os.path.join(top_path, '%02x' % sub)
            if not os.path.exists(sub_path):
                os.mkdir(sub_path)
