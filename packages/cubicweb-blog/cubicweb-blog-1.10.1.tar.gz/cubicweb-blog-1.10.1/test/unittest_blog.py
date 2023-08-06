"""Blog unit tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC, MAILBOX


class BlogTestsCubicWebTC(CubicWebTC):
    """test blog specific behaviours"""

    def test_notifications(self):
        req = self.request()
        cubicweb_blog = req.create_entity('Blog', title=u'cubicweb',
                                          description=u"cubicweb c'est beau")
        blog_entry_1 = req.create_entity('BlogEntry', title=u"hop", content=u"cubicweb hop")
        blog_entry_1.set_relations(entry_of=cubicweb_blog)
        blog_entry_2 = req.create_entity('BlogEntry', title=u"yes",  content=u"cubicweb yes")
        blog_entry_2.set_relations(entry_of=cubicweb_blog)
        self.assertEqual(len(MAILBOX), 0)
        self.commit()
        self.assertEqual(len(MAILBOX), 0)
        blog_entry_1.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        mail = MAILBOX[0]
        self.assertEqual(mail.subject, '[data] hop')
        blog_entry_2.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        self.assertEqual(len(MAILBOX), 2)
        mail = MAILBOX[1]
        self.assertEqual(mail.subject, '[data] yes')

    def test_rss(self):
        req = self.request()
        cubicweb_blog = req.create_entity('Blog', title=u'cubicweb',
                                          description=u"cubicweb c'est beau")
        content = u"""
<style> toto </style> tutu <style class=macin> toto
</style>
tutu
tutu
<style></style>

<tag>tutu</tag>

"""
        blog_entry_1 = req.create_entity('BlogEntry', title=u"hop",
                                         content=content, content_format=u"text/html")
        blog_entry_1.set_relations(entry_of=cubicweb_blog)

        xml = blog_entry_1.view('rssitem')
        self.assertEqual(xml.count("toto"), 0)
        self.assertEqual(xml.count("tutu"), content.count("tutu"))


    def test_prevnext(self):
        req = self.request()
        e1 = req.create_entity('BlogEntry', title=u'a', content=u'a')
        e2 = req.create_entity('CWGroup', name=u'NotTheNextOfe1')
        e3 = req.create_entity('BlogEntry', title=u'b', content=u'b')
        self.commit()
        a1 = e1.cw_adapt_to('IPrevNext')
        self.assertNone(a1.previous_entity())
        self.assertEqual(u'b', a1.next_entity().title)
        a3 = e3.cw_adapt_to('IPrevNext')
        self.assertEqual(u'a', a3.previous_entity().title)
        self.assertNone(a3.next_entity())

if __name__ == '__main__':
    unittest_main()
