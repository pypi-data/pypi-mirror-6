import unittest2 as unittest
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import login

from collective.anonfeedback.testing import\
    COLLECTIVE_ANONFEEDBACK_FUNCTIONAL_TESTING


class TestInstalled(unittest.TestCase):

    layer = COLLECTIVE_ANONFEEDBACK_FUNCTIONAL_TESTING
    
    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    
    def get_browser(self, username=None, password=None):
        browser = Browser(self.app)
        browser.handleErrors = False
        portalURL = self.portal.absolute_url()
        if username:
            browser.open(portalURL + '/login_form')
            browser.getControl(name='__ac_name').value = username
            browser.getControl(name='__ac_password').value = password
            browser.getControl(name='submit').click()
        return browser
        
    def test_views(self):
        """ Validate that our products GS profile has been run and the product 
            installed
        """
        browser = self.get_browser()
        portalURL = self.portal.absolute_url()
        browser.open(portalURL)
        browser.getLink('Give Feedback').click()
        
        form = browser.getForm(name='feedback')
        
        # Submit an incomplete form
        form.getControl('Subject').value = 'Test subject'
        form.getControl('Submit').click()
        self.assertIn('You must enter a subject and some feedback text.', browser.contents)
        # The filled in value remains
        form = browser.getForm(name='feedback')
        self.assertEqual(form.getControl('Subject').value, 'Test subject')
        
        # Complete the form
        form.getControl('Feedback').value = 'Test\nmessage.'
        form.getControl('Submit').click()
        # It worked.
        self.assertIn('Your feedback has been submitted.', browser.contents)
        # Fields should now be empty.
        form = browser.getForm(name='feedback')
        self.assertEqual(form.getControl('Subject').value, '')
        
        # Anonymous people can't view the feedback.
        self.assertNotIn('View Feedback', browser.contents)
        
        # Login
        browser = self.get_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        browser.open(portalURL)
        # Admin *can* see the feedback.
        self.assertIn('View Feedback', browser.contents)
        
        browser.getLink('View Feedback').click()
        
        self.assertIn('<h3>Test subject</h3>', browser.contents)
        