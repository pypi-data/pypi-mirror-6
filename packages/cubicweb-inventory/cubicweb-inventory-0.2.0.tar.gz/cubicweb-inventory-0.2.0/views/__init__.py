"""inventory web user interface"""

from cubicweb.web import uicfg
from cubicweb.web.views.urlrewrite import SimpleReqRewriter
from cubicweb.web import uihelper

uihelper.edit_as_attr('DeviceModel', 'made_by')
uihelper.edit_as_attr('Device', 'model')
uihelper.edit_as_attr('Device', 'supplier')
uihelper.edit_as_attr('Device', 'installed_in')
uihelper.edit_as_attr('Device', 'situated_in')

