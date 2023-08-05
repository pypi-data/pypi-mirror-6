# -*- coding: utf-8 -*-
from moar.thumbnailer import Thumbnailer, DEFAULTS, RESIZE_OPTIONS
import pytest

from .utils import RES_PATH, MockMethod


BASE_URL = 'http://media.example.com'


class MockStorage(object):
    def __init__(self):
        self.get_thumb = MockMethod()
        self.save = MockMethod(return_value='thumb')


class MockEngine(object):
    def __init__(self):
        self.open_image = MockMethod(return_value='im')
        self.close_image = MockMethod()
        self.get_size = MockMethod(return_value=(20, 10))
        self.get_data = MockMethod(return_value='data')
        self.set_orientation = MockMethod(return_value='im')
        self.set_geometry = MockMethod(return_value='im')
        self.apply_filters = MockMethod(return_value='im')


class MockThumb(object):
    pass


def test_new_thumbnailer():
    t = Thumbnailer(RES_PATH, BASE_URL)
    assert t.engine
    assert t.storage
    assert t.storage.base_path == RES_PATH
    assert t.storage.base_url == BASE_URL


def test_parse_path():
    """Test for backwards compatibility.
    """
    t = Thumbnailer(RES_PATH, BASE_URL)

    p = 'test.jpg'
    assert t.parse_path(p) == p

    p = 'asset/003578b2_1.png.370x277_q85_crop-0,0.png'
    assert t.parse_path(p) == p

    p = {
        "name": "b5eec05f48730350cc7ec1cd87de2f9d.jpg",
        "url": "/static/media/images/b5eec05f48730350cc7ec1cd87de2f9d.jpg",
        "relpath": "images",
        "type": "",
        "size": 26444
    }
    assert t.parse_path(p) == 'images/b5eec05f48730350cc7ec1cd87de2f9d.jpg'

    p = {
        "url": "/static/media/photos/home-banner01.jpg",
        "name": "home-banner01.jpg",
        "content_type": "image/jpeg",
        "relpath": "photos"
    }
    assert t.parse_path(p) == 'photos/home-banner01.jpg'


def test_parse_geometry():
    t = Thumbnailer(RES_PATH, BASE_URL)
    assert t.parse_geometry('200x140') == (200, 140)
    assert t.parse_geometry('100') == (100, None)
    assert t.parse_geometry('100x') == (100, None)
    assert t.parse_geometry('x50') == (None, 50)
    assert t.parse_geometry(None) == None
    assert t.parse_geometry(lambda: '20x10') == (20, 10)
    with pytest.raises(ValueError):
        assert t.parse_geometry('axb')


def test_get_key():
    t = Thumbnailer(RES_PATH, BASE_URL)
    #t.get_key(path, geometry, filters, options)

    assert t.get_key('qwertyuiop.jpg', None, [], {}) == t.get_key('qwertyuiop.jpg', None, [], {})
    assert t.get_key('abc.png', (100, 30), [], {}) == \
        '8820aadc6048490c65d46c997d40c2aa'
    assert t.get_key('abc.png', None, [], {}) == \
        '88db0e707dc54b57a5e0c9e52699c6cd'
    assert t.get_key('abc.png', None, [('rotate', 60)], {'format': 'JPEG'}) == \
        '2469c18428fe35fb2422bc94d7acff23'
    assert t.get_key('abc.png', None, [], {'resize': 'fit'}) == \
        'cc88837caa4d797437decd01e187dde1'
    assert t.get_key('abc.png', (100, 30), [], {'resize': 'fit'}) == \
        'a5fde43ca5ab38038805e7687b2c586e'



def test_options():
    t = Thumbnailer(RES_PATH, BASE_URL)
    for k, v in DEFAULTS.items():
        assert getattr(t, k) == v

    t = Thumbnailer(RES_PATH, BASE_URL, format='png')
    assert t.format == 'PNG'

    for r in RESIZE_OPTIONS:
        t = Thumbnailer(RES_PATH, BASE_URL, resize=r)
        assert t.resize == r

    t = Thumbnailer(RES_PATH, BASE_URL, resize='lalala')
    assert t.resize == DEFAULTS['resize']

    new_options = {
        'upscale': False,
        'quality': 80,
        'progressive': False,
        'orientation': False,
    }
    t = Thumbnailer(RES_PATH, BASE_URL, **new_options)
    for k, v in new_options.items():
        assert getattr(t, k) == v


def test_make_thumb():
    s = MockStorage()
    e = MockEngine()
    t = Thumbnailer(RES_PATH, BASE_URL, storage=s, engine=e)
    path = 'abc.jpg'
    geometry = '20x10'
    filters = [('blur', 20), ('crop', '50%', '50%')]
    options = {'format': 'PNG'}
    mthumb = t(path, geometry, *filters, **options)

    assert s.get_thumb.was_called
    assert e.open_image.was_called
    assert e.close_image.was_called
    assert e.get_size.was_called
    assert e.get_data.was_called
    assert e.set_orientation.was_called
    assert e.set_geometry.was_called
    assert e.apply_filters.was_called
    assert s.save.was_called
    assert mthumb == 'thumb'

    assert path in s.get_thumb.args
    assert e.open_image.args[0].endswith(path)
    assert e.get_size.args[0] == 'im'
    assert e.get_data.args[0] == 'im'
    assert e.set_orientation.args[0] == 'im'
    assert e.set_geometry.args[0] == 'im'
    assert e.set_geometry.args[1] == (20, 10)
    assert e.apply_filters.args[0] == 'im'
    assert e.apply_filters.args[1] == filters
    assert 'data' in s.save.args


def test_make_existing_thumb():
    s = MockStorage()
    mock_thumb = MockThumb()
    s.get_thumb = MockMethod(mock_thumb)
    e = MockEngine()
    t = Thumbnailer(RES_PATH, BASE_URL, storage=s, engine=e)
    path = 'abc.jpg'
    geometry = '20x10'
    filters = [('blur', 20)]
    options = {'format': 'PNG'}
    mthumb = t(path, geometry, *filters, **options)

    assert s.get_thumb.was_called
    assert not e.open_image.was_called
    assert not e.close_image.was_called
    assert not e.get_size.was_called
    assert not e.get_data.was_called
    assert not e.set_orientation.was_called
    assert not e.set_geometry.was_called
    assert not e.apply_filters.was_called
    assert not s.save.was_called
    assert mthumb is mock_thumb

