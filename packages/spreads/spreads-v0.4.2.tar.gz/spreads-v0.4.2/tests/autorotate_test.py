import shutil
import tempfile
import unittest

import spreads.vendor.confit as confit
from mock import call, MagicMock as Mock, patch
from spreads.vendor.pathlib import Path

import spreads.util
spreads.util.find_in_path = Mock(return_value=True)
import spreadsplug.autorotate as autorotate


class TestAutorotate(unittest.TestCase):
    def setUp(self):
        self.config = confit.Configuration('test_autorotate')
        self.config['autorotate']['rotate_odd'] = -90
        self.config['autorotate']['rotate_even'] = 90
        self.path = Path(tempfile.mkdtemp())
        (self.path / 'raw').mkdir()

    def tearDown(self):
        shutil.rmtree(unicode(self.path))

    def test_process(self):
        test_files = [self.path / 'raw' / x
                      for x in ('000.jpg', '001.jpg', '002.jpg')]
        map(lambda x: x.touch(), test_files)

        mock_pool = Mock()
        autorotate.futures.ProcessPoolExecutor = Mock(return_value=mock_pool)
        with patch('spreadsplug.autorotate._get_exif_orientation') as geo:
            geo.side_effect = (6, 8, -1)
            plug = autorotate.AutoRotatePlugin(self.config)
            plug.process(self.path)

        assert geo.call_count == 3
        mock_pool.__enter__().submit.assert_has_calls([
            call(autorotate.rotate_image, test_files[0], rotation=90),
            call(autorotate.rotate_image, test_files[1], rotation=-90)
        ])

    def test_process_inverse(self):
        test_files = [self.path / 'raw' / '000.jpg']
        map(lambda x: x.touch(), test_files)
        mock_pool = Mock()
        autorotate.futures.ProcessPoolExecutor = Mock(return_value=mock_pool)
        self.config['autorotate']['rotate_odd'] = 90
        self.config['autorotate']['rotate_even'] = -90
        plug = autorotate.AutoRotatePlugin(self.config)
        with patch('spreadsplug.autorotate._get_exif_orientation') as geo:
            geo.return_value = 6
            plug.process(self.path)
        mock_pool.__enter__().submit.assert_called_with(
            autorotate.rotate_image, test_files[0], rotation=-90
        )

    def test_rotate_image(self):
        mock_img = Mock()
        mock_img.__enter__().height = 200
        mock_img.__enter__().width = 800
        autorotate.wand.image.Image = Mock(return_value=mock_img)
        with patch('spreadsplug.autorotate.subprocess.check_output'):
            autorotate.rotate_image('foo.jpg', 90)
        assert mock_img.__enter__().rotate.call_args_list == [call(90)]
        assert mock_img.__enter__().save.call_args_list == [
            call(filename='foo.jpg')]
