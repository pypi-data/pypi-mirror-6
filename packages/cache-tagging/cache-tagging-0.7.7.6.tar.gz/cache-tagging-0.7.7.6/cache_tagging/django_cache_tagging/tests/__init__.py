# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from uuid import uuid4

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Context, Template
from django.test import TestCase
from django.test.client import RequestFactory

from .. import cache, registry
from ..decorators import cache_transaction_all


class FirstTestModel(models.Model):
    title = models.CharField('title', max_length=255)


class SecondTestModel(models.Model):
    title = models.CharField('title', max_length=255)

CACHES = (
    (FirstTestModel,
     lambda obj: ('tests.firsttestmodel.pk:{0}'.format(obj.pk),
                  'tests.firsttestmodel', ), ),
    (SecondTestModel,
     lambda obj: ('tests.secondtestmodel.pk:{0}'.format(obj.pk), ), ),
)

registry.register(CACHES)


class CacheTaggingTest(TestCase):

    urls = 'cache_tagging.django_cache_tagging.tests.urls'

    def setUp(self):
        self.obj1 = FirstTestModel.objects.create(title='title1')
        self.obj2 = SecondTestModel.objects.create(title='title2')
        if 'cache_tagging.middleware.TransactionMiddleware' in settings.MIDDLEWARE_CLASSES:
            self.OLD_MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES
            settings.MIDDLEWARE_CLASSES = list(self.OLD_MIDDLEWARE_CLASSES)
            settings.MIDDLEWARE_CLASSES.remove('cache_tagging.middleware.TransactionMiddleware')

    def test_cache(self):
        tags1 = ('tests.firsttestmodel.pk:{0}'.format(self.obj1.pk), )
        cache.set('name1', 'value1', tags1, 120)

        tags2 = ('tests.secondtestmodel.pk:{0}'.format(self.obj2.pk),
                 'tests.firsttestmodel', )
        cache.set('name2', 'value2', tags2, 120)

        self.assertEqual(cache.get('name1'), 'value1')
        self.assertEqual(cache.get('name2'), 'value2')

        self.obj1.title = 'title1.2'
        self.obj1.save()
        self.assertEqual(cache.get('name1', None), None)
        self.assertEqual(cache.get('name2', None), None)

        cache.set('name1', 'value1', tags1, 120)
        cache.set('name2', 'value2', tags2, 120)
        self.assertEqual(cache.get('name1'), 'value1')
        self.assertEqual(cache.get('name2'), 'value2')

        self.obj2.title = 'title2.2'
        self.obj2.save()
        self.assertEqual(cache.get('name1'), 'value1')
        self.assertEqual(cache.get('name2', None), None)

        cache.invalidate_tags(*(tags1 + tags2))
        cache.invalidate_tags('non_existen_tag')
        self.assertEqual(cache.get('name1', None), None)

    def test_ancestors(self):
        val1 = cache.get('name1')
        self.assertEqual(val1, None)
        if val1 is None:
            val2 = cache.get('name2')
            self.assertEqual(val2, None)
            if val2 is None:
                val2 = 'val2'
                cache.set('name2', val2, ('tag2', ), 120)
            val1 = 'val1' + val2
            cache.set('name1', val1, ('tag1', ), 120)
        cache.invalidate_tags('tag2')
        self.assertEqual(cache.get('name1'), None)
        self.assertEqual(cache.get('name2'), None)

        cache.set('name2', 'val2', ('tag2', ), 120)
        val1 = cache.get('name1')
        self.assertEqual(val1, None)
        if val1 is None:
            val2 = cache.get('name2')
            self.assertEqual(val2, 'val2')
            if val2 is None:  # val2 is not None, it's only for demonstration
                val2 = 'val2'
                cache.set('name2', val2, ('tag2', ), 120)
            val1 = 'val1' + val2
            cache.set('name1', val1, ('tag1', ), 120)
        cache.invalidate_tags('tag2')
        self.assertEqual(cache.get('name1'), None)
        self.assertEqual(cache.get('name2'), None)

    def test_decorator_cache_page(self):
        resp1 = self.client.get(reverse("cache_tagging_test_decorator"))
        # The first call is blank.
        # Some applications, such as django-localeurl
        # need to activate translation object in middleware.
        resp1 = self.client.get(reverse("cache_tagging_test_decorator"))
        self.assertFalse(resp1.has_header('Expires'))
        self.assertFalse(resp1.has_header('Cache-Control'))
        self.assertFalse(resp1.has_header('Last-Modified'))

        resp2 = self.client.get(reverse("cache_tagging_test_decorator"))
        self.assertFalse(resp2.has_header('Expires'))
        self.assertFalse(resp2.has_header('Cache-Control'))
        self.assertFalse(resp2.has_header('Last-Modified'))
        self.assertEqual(resp1.content, resp2.content)

        cache.invalidate_tags('tests.firsttestmodel')
        resp3 = self.client.get(reverse("cache_tagging_test_decorator"))
        self.assertFalse(resp3.has_header('Expires'))
        self.assertFalse(resp3.has_header('Cache-Control'))
        self.assertFalse(resp3.has_header('Last-Modified'))
        self.assertNotEqual(resp1.content, resp3.content)
        cache.invalidate_tags('tests.firsttestmodel')

    def test_templatetag_nocache(self):
        cache.invalidate_tags('tag1')
        t = Template("""
            {% load cache_tagging_tags %}
            {% cache_tagging cachename|striptags 'tag1' timeout='120' nocache=1 %}
                {{ now }}
                #{% nocache %}
                     if do:
                         context['result'] = 1
                         echo(a + b, '\\n')
                         echo('случай1', '\\n')
                     else:
                         context['result'] = 2
                         echo(b + c, '\\n')
                         echo('случай2', '\\n')
                     echo('<b>bold</b>', '\\n')
                     echo(filters.escape('<b>bold</b>'), '\\n')
                {% endnocache %}#
                and repeat
                {% nocache pickled=3 %}
                     echo('pickled=', pickled, '\\n')
                     nocache.start()
                     echo('nested nocache', '\\n')
                     nocache.end()
                {% endnocache %}
                end
            {% end_cache_tagging %}
            """
        )
        now1 = str(uuid4())
        c = Context({
            'request': RequestFactory().get('/'),
            'cachename': 'nocachename',
            'now': now1,
            'do': True,
            'a': 1,
            'b': 2,
            'c': 3,
            'result': None
        })

        r1 = t.render(c)
        self.assertTrue(now1 in r1)
        self.assertTrue('end' in r1)
        self.assertTrue('#3\n' in r1)
        self.assertTrue('случай1' in r1)
        self.assertEqual(c['result'], 1)
        self.assertTrue('<b>bold</b>' in r1)
        self.assertTrue('&lt;b&gt;bold&lt;/b&gt;' in r1)
        self.assertTrue('pickled=3\n' in r1)
        self.assertTrue('nested nocache\n' in r1)
        self.assertTrue('<nocache' not in r1)

        now2 = str(uuid4())
        c.update({'now': now2, 'do': False})
        r2 = t.render(c)
        self.assertTrue(now1 in r2)
        self.assertTrue(now2 not in r2)
        self.assertTrue('end' in r2)
        self.assertTrue('#5\n' in r2)
        self.assertTrue('случай2' in r2)
        self.assertEqual(c['result'], 2)

        cache.invalidate_tags('tag1')

    def test_templatetag(self):
        t = Template("""
            {% load cache_tagging_tags %}
            {% cache_tagging cachename|striptags tag1|striptags 'tests.secondtestmodel' tags=empty_val|default:tags timeout='120' %}
                {{ now }}
                {% cache_add_tags tag3 %}
            {% end_cache_tagging %}
            """
        )
        c = Context({
            'request': RequestFactory().get('/'),
            'now': uuid4(),
            'cachename': 'cachename',
            'tag1': 'tests.firsttestmodel',
            'tag3': 'tag3',
            'empty_val': '',
            'tags': ['tests.secondtestmodel.pk:{0}'.format(self.obj2.pk), ],
        })

        # Case 1
        # Tags from arguments.
        r1 = t.render(c)
        self.assertTrue(hasattr(c['request'], 'cache_tagging'))
        self.assertTrue('tests.firsttestmodel' in c['request'].cache_tagging)
        self.assertTrue('tests.secondtestmodel.pk:{0}'.format(self.obj2.pk)\
                        in c['request'].cache_tagging)
        self.assertTrue('tag3' in c['request'].cache_tagging)

        c.update({'now': uuid4(), })
        r2 = t.render(c)
        self.assertEqual(r1, r2)

        cache.invalidate_tags('tests.firsttestmodel')
        c.update({'now': uuid4(), })
        r3 = t.render(c)
        self.assertNotEqual(r1, r3)

        # Case 2
        # Tags from keyword arguments.
        c.update({'now': uuid4(), })
        r4 = t.render(c)
        self.assertEqual(r3, r4)

        cache.invalidate_tags('tests.secondtestmodel.pk:{0}'.format(self.obj2.pk))
        c.update({'now': uuid4(), })
        r5 = t.render(c)
        self.assertNotEqual(r3, r5)

        # Case 3
        # Tags from templatetag {% cache_add_tags %}
        c.update({'now': uuid4(), })
        r6 = t.render(c)
        self.assertEqual(r5, r6)

        cache.invalidate_tags('tag3')
        c.update({'now': uuid4(), })
        r7 = t.render(c)
        self.assertNotEqual(r5, r7)

        cache.invalidate_tags('tag3',
                              'tests.firsttestmodel',
                              'tests.secondtestmodel.pk:{0}'.format(self.obj2.pk))

    def test_templatetag_prevent(self):
        t = Template("""
            {% load cache_tagging_tags %}
            {% cache_tagging cachename|striptags tag1|striptags 'tests.secondtestmodel' tags=empty_val|default:tags timeout='120' %}
                {{ now }}
                {% cache_add_tags tag3 "tag4" %}
                {% cache_tagging_prevent %}
            {% end_cache_tagging %}
            """
        )
        c = Context({
            'request': RequestFactory().get('/'),
            'now': uuid4(),
            'cachename': 'cachename',
            'tag1': 'tests.firsttestmodel',
            'tag3': 'tag3',
            'empty_val': '',
            'tags': ['tests.secondtestmodel.pk:{0}'.format(self.obj2.pk), ],
        })

        r1 = t.render(c)
        self.assertTrue(hasattr(c['request'], 'cache_tagging'))
        self.assertTrue('tests.firsttestmodel' in c['request'].cache_tagging)
        self.assertTrue('tests.secondtestmodel.pk:{0}'.format(self.obj2.pk)\
                        in c['request'].cache_tagging)
        self.assertTrue('tag3' in c['request'].cache_tagging)
        self.assertTrue('tag4' in c['request'].cache_tagging)
        self.assertTrue(hasattr(c['request'], '_cache_update_cache'))

        c.update({'now': uuid4(), })
        r2 = t.render(c)
        self.assertNotEqual(r1, r2)
        self.assertTrue(hasattr(c['request'], '_cache_update_cache'))

        c.update({'now': uuid4(), })
        r3 = t.render(c)
        self.assertNotEqual(r2, r3)
        self.assertTrue(hasattr(c['request'], '_cache_update_cache'))

    def test_cache_transaction_handlers(self):
        with cache.transaction:
            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name1'), 'value1')

            with cache.transaction:
                cache.set('name2', 'value2', ('tag2', ), 120)
                self.assertEqual(cache.get('name2'), 'value2')

                cache.invalidate_tags('tag2')
                self.assertEqual(cache.get('name2', None), None)
                self.assertEqual(cache.get('name1'), 'value1')

                cache.set('name2', 'value2', ('tag2', ), 120)
                self.assertEqual(cache.get('name2'), 'value2')
                self.assertEqual(cache.get('name1'), 'value1')

            self.assertEqual(cache.get('name2', None, abort=True), None)
            self.assertEqual(cache.get('name1'), 'value1')

            cache.set('name3', 'value3', ('tag3', ), 120)
            self.assertEqual(cache.get('name3'), 'value3')
            self.assertEqual(cache.get('name1'), 'value1')

            cache.invalidate_tags('tag1')
            self.assertEqual(cache.get('name3'), 'value3')
            self.assertEqual(cache.get('name1', None), None)

            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name3'), 'value3')
            self.assertEqual(cache.get('name1'), 'value1')

        self.assertEqual(cache.get('name3'), 'value3')
        self.assertEqual(cache.get('name1', None), None)

        # tests for cache.transaction.flush()
        cache.transaction.begin()  # 1
        cache.transaction.begin()  # 2
        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        cache.invalidate_tags('tag1')
        self.assertEqual(cache.get('name1', None), None)
        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        cache.transaction.begin()  # 3
        cache.transaction.begin()  # 4

        cache.transaction.flush()  # all
        self.assertEqual(cache.get('name1', None), None)

        cache.invalidate_tags('tag1', 'tag2', 'tag3')

    def test_cache_transaction_context(self):
        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        with cache.transaction:
            cache.invalidate_tags('tag1')
            self.assertEqual(cache.get('name1', None), None)
            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name1'), 'value1')
        self.assertEqual(cache.get('name1', None), None)

    def test_cache_transaction_decorator(self):
        @cache.transaction
        def some_func():
            cache.invalidate_tags('tag1')
            self.assertEqual(cache.get('name1', None), None)
            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name1'), 'value1')

        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        some_func()
        self.assertEqual(cache.get('name1', None), None)

    def test_cache_transaction_decorator2(self):
        @cache.transaction()
        def some_func():
            cache.invalidate_tags('tag1')
            self.assertEqual(cache.get('name1', None), None)
            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name1'), 'value1')

        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        some_func()
        self.assertEqual(cache.get('name1', None), None)

    def test_cache_transaction_decorator_all(self):
        @cache_transaction_all
        def some_func():
            cache.transaction.begin()
            cache.invalidate_tags('tag1')
            cache.transaction.begin()
            self.assertEqual(cache.get('name1', None), None)
            cache.set('name1', 'value1', ('tag1', ), 120)
            self.assertEqual(cache.get('name1'), 'value1')

        cache.transaction.begin()
        cache.transaction.begin()
        cache.set('name1', 'value1', ('tag1', ), 120)
        self.assertEqual(cache.get('name1'), 'value1')
        some_func()
        self.assertEqual(cache.get('name1', None), None)

    def tearDown(self):
        if hasattr(self, 'OLD_MIDDLEWARE_CLASSES'):
            settings.MIDDLEWARE_CLASSES = self.OLD_MIDDLEWARE_CLASSES
