import time
from datetime import datetime, timedelta
from json import loads, dumps
from urllib import quote_plus
import urllib2
from five import grok
from z3c.form import button
from AccessControl.PermissionRole import rolesForPermissionOn
from plone.directives import form
from plone.behavior.annotation import AnnotationsFactoryImpl
from Products.CMFPlone.log import log
from Products.statusmessages.interfaces import IStatusMessage

from .config import DEBUG
from .interfaces import IZoomItImage, IZoomItInfo
from . import MessageFactory as _


ZOOMIT_UPLOAD_URL = 'http://api.zoom.it/v1/content/'
SAMPLE_DEBUG_IMAGE = 'http://imaging.nikon.com/lineup/dslr/d90/img/sample/pic_003b.jpg'
UPDATE_WAIT = 300 # 5 minutes

opener = urllib2.OpenerDirector()
opener.add_handler(urllib2.HTTPHandler())
opener.add_handler(urllib2.HTTPDefaultErrorHandler())


class ZoomItAdapter(AnnotationsFactoryImpl, grok.Adapter):
    grok.context(IZoomItImage)
    grok.provides(IZoomItInfo)

    def __init__(self, context):
        super(ZoomItAdapter, self).__init__(context, IZoomItInfo)
        self.context = context

    def _set_content(self, response):
        self.last_status = response.getcode()
        data = loads(response.read())
        self.id = data['id']
        self.url = data['shareUrl']
        self.ready = data['ready']
        self.failed = data['failed']
        self.progress = data['progress']
        self.embed = data['embedHtml']
        if data.get('dzi', None) and data['dzi'].get('url', None):
            self.dzi = data['dzi']['url']
        self.retry_after = None

    @property
    def api_url(self):
        if self.id:
            return ZOOMIT_UPLOAD_URL + self.id

    @property
    def image_url(self):
        return self.context.absolute_url() + '/@@images/image'

    @property
    def image_modified(self):
        context = self.context
        if hasattr(context, 'getImage'):
            image = context.getImage()
        else:
            image = getattr(context, 'image', None)
        if image is not None:
            # We should be able to use the NamedFile or BlobWrapper mtime
            # to check for image replacement.
            mtime = image._p_mtime
            if mtime is not None:
                return datetime.fromtimestamp(mtime)
            return datetime.now()
        return None

    def create_content(self):
        # We can only initiate if the image is publicly visible
        if 'Anonymous' not in rolesForPermissionOn('View', self.context):
            # Reset
            self.ready = None
            self.id = None
            return
        image_url = self.image_url
        is_local = '://localhost:' in image_url or '://127.' in image_url
        if DEBUG and is_local:
            image_url = SAMPLE_DEBUG_IMAGE
        elif is_local:
            return

        if self.ready:
            # Updating an already processed image, we need to force a
            # new URL (and avoid possible front-end caches)
            image_url = '%s?cachebust=%s'%(image_url, time.time())

        request = urllib2.Request('%s?url=%s'%(ZOOMIT_UPLOAD_URL,
                                               quote_plus(image_url)),
                                  headers={"Accept" : "application/json"})
        try:
            response = opener.open(request)
        except urllib2.HTTPError, response:
            pass
        code = response.getcode()
        if code == 301:
            info = response.info()
            self._set_content(response)
            assert self.api_url == info['Location']
        else:
            data = response.read()
            headers = response.info()
            retry_after = headers.get('Retry-After')
            if retry_after:
                try:
                    retry_after = int(retry_after)
                except (ValueError, TypeError):
                    retry_after = None
            log('Zoomit create call failed for %s: %s, %s' % (
                image_url,
                code,
                data))
            self.failed = True
            self.last_status = code
            if retry_after:
                log('Retry after %s seconds' % retry_after)
                self.last_response = (data +
                                      ('\n Retry after %s seconds' %
                                       retry_after))
            else:
                self.last_response = data
            self.retry_after = retry_after
        self.update_timestamp = datetime.now()

    def update_status(self):
        if not self.api_url:
            return
        request = urllib2.Request(self.api_url,
                                  headers={"Accept" : "application/json"})
        try:
            response = opener.open(request)
        except urllib2.HTTPError, response:
            pass
        code = response.getcode()
        if code in (200, 301, 302):
            self._set_content(response)
        else:
            data = response.read()
            headers = response.info()
            retry_after = headers.get('Retry-After')
            if retry_after:
                try:
                    retry_after = int(retry_after)
                except (ValueError, TypeError):
                    retry_after = None
            log('Zoomit update call failed %s: %s, %s' % (
                self.context.absolute_url(),
                code,
                data))
            self.failed = True
            self.status = code
            if retry_after:
                log('Retry after %s seconds' % retry_after)
                self.last_response = (data +
                                      ('\n Retry after %s seconds' %
                                       retry_after))
            else:
                self.last_response = data
            self.retry_after = retry_after
        self.update_timestamp = datetime.now()


class ZoomItUpdater(form.Form):
    grok.context(IZoomItImage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('zoomit-updater')

    label = _(u'Zoom.it Information')

    def update(self):
        if not self._show_create():
            IStatusMessage(self.request).addStatusMessage(
                _(u'Cannot initialize zoom.it on unpublished images'))
        super(ZoomItUpdater, self).update()
        self.info = IZoomItInfo(self.context)

    def _redirect_to_self(self):
        self.request.response.redirect(self.request.ACTUAL_URL)

    def _show_update(self):
        info = IZoomItInfo(self.context)
        return bool(info.api_url) and not info.ready

    def _show_create(self):
        return 'Anonymous' in rolesForPermissionOn('View', self.context)

    @button.buttonAndHandler(u'Update Status', condition=_show_update)
    def update_image(self, action):
        zoomit_info = IZoomItInfo(self.context)
        zoomit_info.update_status()
        if zoomit_info.failed:
            resp = zoomit_info.last_response or 'try again later.'
            IStatusMessage(self.request).addStatusMessage(
                _(u'Zoom.it service returned an error response (%d), %s'%(
                zoomit_info.last_status, resp)))
        else:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Status update succeeded'))
        self._redirect_to_self()
        return ''

    @button.buttonAndHandler(u'Recreate Image', condition=_show_create)
    def create_image(self, action):
        zoomit_info = IZoomItInfo(self.context)
        zoomit_info.create_content()
        if zoomit_info.failed:
            resp = zoomit_info.last_response or 'try again later.'
            IStatusMessage(self.request).addStatusMessage(
                _(u'Zoom.it service returned an error response (%d), %s'%(
                zoomit_info.last_status, resp)))
        elif zoomit_info.id:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Image creation succeeded'))
            if not zoomit_info.ready:
                IStatusMessage(self.request).addStatusMessage(
                _(u'The item must stay published while waiting to process the image'))
        else:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Unable to create image, ensure that the image is publicly '
                  'visible from the hostname you are using.'))
        self._redirect_to_self()
        return ''


class ZoomItJSON(grok.View):
    grok.context(IZoomItImage)
    grok.require('zope2.View')
    grok.name('zoomit-json')

    def update(self, **kw):
        self.info = IZoomItInfo(self.context)
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        # Check if the widget is ready
        wait_time = timedelta(seconds=self.info.retry_after or UPDATE_WAIT)
        if (not self.info.ready and self.info.update_timestamp
                and (datetime.now() - self.info.update_timestamp) < wait_time):
            # We perform a write operation on a GET here, but only if
            # the image is not ready and at most once every 10 minutes
            self.info.update_status()

    def render(self, **kw):
        response = {}
        response['ready'] = bool(self.info.ready)
        response['embed'] = self.info.embed or ''
        response['image_url'] = self.info.image_url
        response['id'] = self.info.id
        return dumps(response)


# Update or create as needed on add, edit and workflow change
def update_on_edit(context, event):
    info = IZoomItInfo(context)
    image_modified = info.image_modified
    if image_modified is not None:
        # Create if not yet created or image was modified in the last 3 seconds
        wait_time = timedelta(seconds=info.retry_after or UPDATE_WAIT)
        now = datetime.now()
        if ((not info.id and not info.update_timestamp) or (not info.id and
            (now - info.update_timestamp) < wait_time)) or (
                (now - image_modified) <= timedelta(seconds=3)):
            info.create_content()
        elif info.id and not info.ready:
            info.update_status()
    else:
        # Image not present, reset status
        info.id = None
        info.ready = None
