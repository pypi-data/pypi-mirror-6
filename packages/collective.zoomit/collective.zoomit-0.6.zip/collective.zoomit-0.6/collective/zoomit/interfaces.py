from zope.interface import Interface
from zope import schema
from . import MessageFactory as _


class IZoomItImage(Interface):
    """An behavior/marker for content implementing zoomit API integration"""


class IZoomItInfo(Interface):

    id = schema.TextLine(title=_(u'Zoom.it ID'))

    url = schema.URI(title=_(u'Zoom.it URL'))

    ready = schema.Bool(title=_(u'Upload Ready'))

    progress = schema.Float(title=_(u'Upload Progress'))

    failed = schema.Bool(title=_(u'Upload Failure?'))

    last_status = schema.Int(title=_(u'Last Response Status'))
    last_response = schema.Int(title=_(u'Last Response'),
                               required=False)

    update_timestamp = schema.Datetime(title=_(u'Last Timestamp'),
                                       required=False)

    embed = schema.Text(title=_(u'Embed HTML'))

    dzi = schema.URI(title=_(u'DZI URL'),
                     required=False)

    image_url = schema.URI(title=_(u'Image URL'),
                           readonly=True)

    image_modified = schema.Datetime(title=_(u'Image Last Modified'),
                                     readonly=True,
                                     required=False)

    api_url = schema.URI(title=_(u'DZI URL'),
                         readonly=True)

    def create_content(self):
        """Initializes zoom.it content"""

    def update_status(self):
        """Updates status of zoomit content"""


