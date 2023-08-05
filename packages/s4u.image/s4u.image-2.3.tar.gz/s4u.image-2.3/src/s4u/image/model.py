try:
    from cStringIO import StringIO as BytesIO
except ImportError:  # pragma: no cover
    # Python 3
    from io import BytesIO
import io
import os
import uuid
import requests
from sqlalchemy import schema
from sqlalchemy import types
from sqlalchemy.orm.session import object_session
from repoze.filesafe import create_file
from repoze.filesafe import open_file
from repoze.filesafe import delete_file
from s4u.sqlalchemy.meta import BaseObject
from s4u.image.util import extension_for_image_data
from s4u.image.scale import scale_image


def generate_path(extension):
    """Generate a filename within the image storage. The is based on a
    random string and the given extension. A three-level directory
    structure is used.
    """
    filename = '%s%s' % (uuid.uuid4(), extension)
    filename = os.path.join(filename[0], filename[1:3], filename)
    return filename


class Image(BaseObject):
    """A source image.
    """
    root_path = None
    __tablename__ = 'image'

    id = schema.Column(types.Integer(),
            schema.Sequence('image_id_seq', optional=True),
            primary_key=True, autoincrement=True)
    #: Relative filesystem path for the image
    path = schema.Column(types.String(128), unique=True)
    #: URL for (canonical) image.
    url = schema.Column(types.Text())

    def __init__(self, data=None, filename=None, url=None):
        if not (data is not None or url is not None):
            raise ValueError('You must provide at least one of data or url')
        self.url = url
        if data is not None:
            self._set_content(data, filename)

    @property
    def filesystem_path(self):
        """Return the (absolute) filesystem path for the image data."""
        if self.root_path is None:
            raise AttributeError('root_path not set')
        if not self.path:
            return None
        return os.path.join(self.root_path, self.path)

    def download(self, timeout=0.5):  # pragma: no cover
        """Download a remote image so we have a local copy.
        """
        if self.path is not None:
            raise TypeError('Image already has local data.')
        r = requests.get(self.url, timeout=timeout)
        extension = extension_for_image_data(BytesIO(r.content))
        self.path = generate_path(extension)
        file = create_file(self.filesystem_path, 'wb')
        if hasattr(file, 'fileno'):  # pragma: no cover (for testing only)
            try:
                os.fchmod(file.fileno(), 0o644)
            except io.UnsupportedOperation:  # BytesIO for testing
                pass
        file.write(r.content)
        file.close()

    def scale(self, width=None, height=None, crop=False,
            strip_whitespace=False):
        """Return a scaled version of this image. If a matching
        :py:class:`ImageScale` is found it is returned directly.  Otherwise the
        image will be scaled and a new ImageScale instance is created.

        See :py:func:`scale_image <s4u.image.scale.scale_image>` for more
        information on the scaling parameters.

        :rtype: :py:class:`ImageScale`
        """
        if not self.path:
            raise TypeError('Can not scale an image that is not stored locally.')

        if not (width or height):
            raise ValueError('You must specify either width or height')

        session = object_session(self)
        scale = session.query(ImageScale)\
                .filter(ImageScale.image_id == self.id)\
                .filter(ImageScale.param_width == (width or 0))\
                .filter(ImageScale.param_height == (height or 0))\
                .filter(ImageScale.param_crop == crop)\
                .filter(ImageScale.param_strip_whitespace == strip_whitespace)\
                .first()
        if scale is None:
            scale = ImageScale(self, width, height, crop, strip_whitespace)
            session.add(scale)
        return scale

    def delete(self):
        """Delete this image including all scales from the database and disk.
        """
        self._delete_scales()
        delete_file(self.filesystem_path)
        object_session(self).delete(self)

    def replace(self, data, filename=None):
        """Replace the image contents.

        This method should be used to modify images. This method will
        delete old old image scales and switch to a new filename and
        URL.

        :param str data: Raw image data.
        :param str filename: Image filename (optional)

        """
        self._delete_scales()
        delete_file(self.filesystem_path)
        self._set_content(data, filename)

    def _set_content(self, data, filename=None):
        extension = None
        if filename:
            extension = os.path.splitext(filename)[1]
        if not extension:
            extension = extension_for_image_data(BytesIO(data))
        self.path = generate_path(extension)
        file = create_file(self.filesystem_path, 'wb')
        if hasattr(file, 'fileno'):  # pragma: no cover (for testing only)
            try:
                os.fchmod(file.fileno(), 0o644)
            except io.UnsupportedOperation:  # BytesIO for testing
                pass
        file.write(data)
        file.close()

    def _delete_scales(self):
        """Remove all existing image scales.
        """
        session = object_session(self)
        scales = session.query(ImageScale).filter(ImageScale.image_id == self.id)
        for scale in scales:
            delete_file(scale.filesystem_path)
        scales.delete()


class ImageScale(BaseObject):
    """A scaled version of image. Each :obj:`Image` can have many different
    scaled versions. The final dimensions of the image are stored to allow
    efficient creation of HTML ``img`` tags.
    """
    root_path = None
    __tablename__ = 'image_scale'
    __table_args__ = (
            schema.UniqueConstraint('image_id',
                                    'param_width', 'param_height',
                                    'param_crop', 'param_strip_whitespace'),
            schema.CheckConstraint('param_width>0 or param_height>0'),
            {})

    id = schema.Column(types.Integer(),
            schema.Sequence('image_scale_id_seq', optional=True),
            primary_key=True, autoincrement=True)
    path = schema.Column(types.String(128), nullable=False, unique=True)
    image_id = schema.Column(types.Integer(),
            schema.ForeignKey(Image.id,
                ondelete='CASCADE', onupdate='CASCADE'),
            nullable=False)
    param_width = schema.Column(types.Integer(), nullable=False)
    param_height = schema.Column(types.Integer(), nullable=False)
    param_crop = schema.Column(types.Boolean(), nullable=False)
    param_strip_whitespace = schema.Column(types.Boolean(), nullable=False)

    #: The width in pixels of the scaled image.
    width = schema.Column(types.Integer(), nullable=False)
    #: The heighy in pixels of the scaled image.
    height = schema.Column(types.Integer(), nullable=False)

    def __init__(self, image, width=None, height=None, crop=False,
            strip_whitespace=False):
        self.image_id = image.id
        self.param_width = width or 0
        self.param_height = height or 0
        self.param_crop = crop
        self.param_strip_whitespace = strip_whitespace

        file = open_file(image.filesystem_path, 'wb')
        (data, format, size) = scale_image(file, width, height, crop,
                strip_whitespace)
        self.path = generate_path('.' + format.lower())
        self.width = size[0]
        self.height = size[1]
        file = create_file(self.filesystem_path, 'wb')
        if hasattr(file, 'fileno'):  # pragma: no cover (for testing only)
            try:
                os.fchmod(file.fileno(), 0o644)
            except io.UnsupportedOperation:  # BytesIO for testing
                pass
        file.write(data)
        file.close()

    @property
    def filesystem_path(self):
        """Return the (absolute) filesystem path for the image data."""
        if self.root_path is None:
            raise AttributeError('root_path not set')
        return os.path.join(self.root_path, self.path)

    def _delete(self):
        """Remove image scale from database and filesystem.
        """
        delete_file(self.filesystem_path)
        object_session(self).delete(self)


schema.Index('image_scale_parameters',
             ImageScale.image_id,
             ImageScale.param_width,
             ImageScale.param_height,
             ImageScale.param_crop,
             ImageScale.param_strip_whitespace)

__all__ = ['Image', 'ImageScale']
