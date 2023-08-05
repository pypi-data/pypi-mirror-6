from five import grok
from plone.app.layout.viewlets.interfaces import IAboveContent
from plone.app.layout.globals.interfaces import IViewView

from .interfaces import IZoomItImage

class ZoomItSnippet(grok.Viewlet):
    grok.viewletmanager(IAboveContent)
    grok.context(IZoomItImage)
    grok.view(IViewView)

    def available(self):
        return True

    def render(self):
        """Returns a simple marker span"""
        return '<span id="zoomit-marker" />'
