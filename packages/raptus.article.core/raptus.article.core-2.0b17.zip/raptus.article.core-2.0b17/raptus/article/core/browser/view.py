from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.globals.interfaces import IViewView

from raptus.article.core import interfaces


class View(BrowserView):
    """View of an article
    """
    implements(interfaces.IArticleView, IViewView)
    template = ViewPageTemplateFile('view.pt')

    def __call__(self):
        self.request.set('raptus_article_viewing', True)
        return self.template()
