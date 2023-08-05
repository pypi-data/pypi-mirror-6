# -*- coding: utf-8 -*-
import unittest2 as unittest
import os
from zope.interface import alsoProvides
from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from wildcard.media.interfaces import IVideoEnabled

from wildcard.media.testing import (
    MEDIA_INTEGRATION_TESTING,
    MEDIA_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.z3cform.interfaces import IPloneFormLayer
from wildcard.media.tests import getVideoBlob, test_file_dir
from wildcard.media.settings import GlobalSettings


class VideoIntegrationTest(unittest.TestCase):

    layer = MEDIA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        settings = GlobalSettings(self.portal)
        settings.additional_video_formats = []

    def getFti(self):
        return queryUtility(IDexterityFTI, name='WildcardVideo')

    def create(self, id):
        self.portal.invokeFactory('WildcardVideo', id,
                                  video_file=getVideoBlob())

    def test_schema(self):
        fti = self.getFti()
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_WildcardVideo')

    def test_fti(self):
        fti = self.getFti()
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = self.getFti()
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IVideoEnabled.providedBy(new_object))

    def test_adding(self):
        self.create('video1')
        self.assertTrue(IVideoEnabled.providedBy(self.portal['video1']))

    def test_view(self):
        self.create('video2')
        video = self.portal['video2']
        video.title = "My video"
        video.description = "This is my video."
        self.request.set('URL', video.absolute_url())
        self.request.set('ACTUAL_URL', video.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)
        view = video.restrictedTraverse('@@view')

        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue('My video' in view())
        self.assertTrue('This is my video.' in view())


class VideoFunctionalTest(unittest.TestCase):

    layer = MEDIA_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        settings = GlobalSettings(self.portal)
        settings.additional_video_formats = []
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_video(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Video').click()
        self.browser.getControl(
            name='form.widgets.IDublinCore.title').value = "My video"
        self.browser.getControl(
            name='form.widgets.IDublinCore.description')\
            .value = "This is my video."
        file_path = os.path.join(test_file_dir, "test.mp4")
        file_ctl = self.browser.getControl(
            name='form.widgets.IVideo.video_file')
        file_ctl.add_file(open(file_path), 'video/mp4', 'test.mp4')
        self.browser.getControl('Save').click()
        self.assertTrue('My video' in self.browser.contents)
        self.assertTrue('This is my video' in self.browser.contents)
        self.assertTrue('<video' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
