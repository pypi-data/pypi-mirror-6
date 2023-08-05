import unittest
try:
    from cStringIO import StringIO as BytesIO
except ImportError:  # pragma: no cover
    # Python 3
    from io import BytesIO


class extension_for_image_data_tests(unittest.TestCase):
    def extension_for_image_data(self, *a, **kw):
        from s4u.image.util import extension_for_image_data
        return extension_for_image_data(*a, **kw)

    def test_invalid_image(self):
        input = BytesIO(b'invalid')
        self.assertRaises(ValueError,
                self.extension_for_image_data, input)

    def test_minimal_gif(self):
        from s4u.image.testing import GIF
        input = BytesIO(GIF)
        self.assertEqual(self.extension_for_image_data(input), '.gif')

    def test_minimal_png(self):
        from s4u.image.testing import PNG
        input = BytesIO(PNG)
        self.assertEqual(self.extension_for_image_data(input), '.png')
