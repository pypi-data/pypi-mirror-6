# -*- coding: utf-8 -*-
import os

from testtools import TestCase
from . import makeprefs, dummykey, _temp_home
from shutil import copy
from mock import patch, Mock
from contextlib import nested


class CacheTest(TestCase):
    def setUp(self):
        super(CacheTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(CacheTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.cache import Cache
        return Cache(*args, **kwargs)

    def test_cache(self):
        assert self._makeit("")

    def test_prepare(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            cache.prepare('foo', os.path.join('t', 'data', 'arc1'))
            archives = cache._for_adf('archives')
            self.assertEqual(len(archives), 1)
            self.assertEqual('foo',
                             next(archives.itervalues())['archive'].title)

    def test_cache_dir(self):
        d = 'archives'
        self.assertTrue(
            os.path.isdir(self._makeit(self.home)._cache_dir(d)))
        with _temp_home() as home:
            cache = self._makeit(home)
            self.assertFalse(os.path.exists(cache._cache_dir(d)))
            self.assertTrue(os.path.isdir(cache._cache_dir(d, write=True)))

    def test_archive_open(self):
        open_mock = Mock(return_value=None)
        import lacli.cache as cache
        with patch.object(cache, 'open', open_mock, create=True):
            with _temp_home() as home:
                cache = self._makeit(home)
                dname = os.path.join(home, 'archives')
                fname = os.path.join(dname, 'foo')
                cache._archive_open('foo', 'w')
                open_mock.assert_called_with(fname, 'w')
                self.assertTrue(os.path.isdir(dname))
                cache._cert_open('foo', 'w')
                dname = os.path.join(home, 'certs')
                fname = os.path.join(dname, 'foo')
                open_mock.assert_called_with(fname, 'w')
                self.assertTrue(os.path.isdir(dname))

    def test_certs(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            self.assertEqual({}, cache.certs())
            cdir = os.path.join(home, 'certs')
            os.makedirs(cdir)
            certs = cache.certs()
            self.assertEqual(0, len(certs))
            copy(os.path.join(self.home, 'archives', 'sample.adf'), cdir)
            certs = cache.certs()
            self.assertEqual(1, len(certs))
            self.assertIn('12-345', certs)
            self.assertIn('archive', certs['12-345'])
            self.assertEqual('My 2013 vacation',
                             certs['12-345']['archive'].title)
            c = certs['12-345']['cert'].keys[1]
            self.assertTrue(hasattr(c, 'key'))
            self.assertTrue(hasattr(c, 'method'))
            self.assertTrue(hasattr(c, 'input'))
            self.assertEqual(dummykey, c.input)
            self.assertEqual(1, c.key)
            self.assertEqual('pbkdf2', c.method)

    def test_save_cert(self):
        import lacli.cache
        from lacli.adf import Archive, Meta, Signature
        from StringIO import StringIO
        with nested(
                patch.object(lacli.cache, 'NamedTemporaryFile', create=True),
                patch.object(lacli.cache, 'archive_slug', create=True),
                ) as (mock_open, slug):
            mock_open.return_value.__enter__.return_value = StringIO()
            meta = Meta('zip', 'xor', created='now')
            archive = Archive('foo', meta)
            slug.return_value = 'foo'
            cache = self._makeit(self.home)
            cache.save_cert({'archive': archive,
                             'signature': Signature(aid="foo",
                                                    uri="http://baz.com",
                                                    created="now")})
            args, kwargs = mock_open.call_args
            self.assertIn('prefix', kwargs)
            self.assertEqual('foo', kwargs['prefix'])
            adf = mock_open.return_value.__enter__.return_value.getvalue()
            self.assertEqual(ADF_EXAMPLE_1, adf)

    def test_import_cert(self):
        import lacli.cache
        from StringIO import StringIO
        with nested(
                patch.object(lacli.cache, 'NamedTemporaryFile', create=True),
                patch.object(lacli.cache, 'archive_slug', create=True),
                _temp_home()
                ) as (mock_open, slug, home):
            mock_open.return_value.__enter__.return_value = StringIO()
            slug.return_value = 'foo'
            cache = self._makeit(home)
            cert = os.path.join('t', 'data', 'longaccess-74-5N93.html')
            aid = cache.import_cert(cert)
            args, kwargs = mock_open.call_args
            self.assertIn('prefix', kwargs)
            self.assertEqual('foo', kwargs['prefix'])
            self.assertEqual('74-5N93', aid)

    def test_upload_complete(self):
        import lacli.cache
        cache = self._makeit(self.home)
        with nested(
                patch.object(lacli.cache, 'open', create=True),
                patch.object(lacli.cache, 'load_archive', create=True),
                patch.object(lacli.cache, 'make_adf', create=True)
                ) as (mock_open, mock_load, mock_adf):
            mock_load.return_value = {}
            ds = cache.upload_complete("foo", {'archive_key': 'bar'})
            self.assertIn('signature', ds)
            self.assertEqual('bar', ds['signature'].aid)
            self.assertEqual('http://longaccess.com/a/', ds['signature'].uri)
            args, kwargs = mock_adf.call_args
            self.assertEqual('bar', args[0][0].aid)


ADF_EXAMPLE_1 = """!archive
meta: !meta {cipher: xor, created: now, format: zip}
title: foo
--- !signature {aid: foo, created: now, uri: 'http://baz.com'}
"""
