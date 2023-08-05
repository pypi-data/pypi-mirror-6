

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FGStringFieldPermissionsView(BrowserView):
    """ Default view of a registrant """    
    __call__ = ViewPageTemplateFile('fgstringfieldpermission.pt')

