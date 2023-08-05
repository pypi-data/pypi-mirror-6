from collective.oembed.tests import base


class Test(base.UnitTestCase):

    def setUp(self):
        super(Test, self).setUp()
        from collective.oembed import viewlet
        self.viewlet = viewlet.Discovery(self.context,
                                         self.request, None)
        self.viewlet.site_url = 'http://nohost'

    def test_oembed_url_json(self):
        url = self.viewlet.oembed_url_json()
        shouldbe = u'http://nohost/@@oembed?url=http%3A%2F%2Fnohost.com%2Fmyid'
        shouldbe += u'&format=json'
        self.assertEqual(url, shouldbe)

    def test_oembed_url_xml(self):
        url = self.viewlet.oembed_url_xml()
        shouldbe = u'http://nohost/@@oembed?url=http%3A%2F%2Fnohost.com%2Fmyid'
        shouldbe += u'&format=xml'
        self.assertEqual(url, shouldbe)

    def test_title(self):
        title = self.viewlet.title()
        self.assertTrue(title.endswith('oEmbed Profile'))

    def test_query(self):
        query = self.viewlet.query()
        self.assertIn('url', query)
        self.assertEqual(query['url'], self.context.absolute_url())


class TestIntegration(base.TestCase):

    def setUp(self):
        super(TestIntegration, self).setUp()
        from collective.oembed import viewlet
        self.viewlet = viewlet.Discovery(self.portal,
                                         self.portal.REQUEST, None)
        self.viewlet.site_url = 'http://nohost'

    def test_rendering(self):
        import re
        text = self.viewlet.render()
        json_re = '<link rel="alternate" type="application/json\+oembed" '
        json_re += 'href=".*" title=".*" />'
        xml_re = '<link rel="alternate" type="text/xml\+oembed" href=".*" '
        xml_re += 'title=".*" />'
        self.assertTrue(re.search(json_re, text) is not None)
        self.assertTrue(re.search(xml_re, text) is not None)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    return base.build_test_suite((Test, TestIntegration))
