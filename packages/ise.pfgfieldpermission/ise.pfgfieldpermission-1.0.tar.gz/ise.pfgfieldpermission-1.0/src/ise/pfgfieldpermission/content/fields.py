from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from Products.Archetypes.interfaces import IObjectPostValidation

from Products.Archetypes import atapi
from Products.Archetypes.browser.validation import InlineValidationView  

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

# From PloneFormGen
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.fieldsBase import BaseFieldSchemaStringDefault
from Products.PloneFormGen.content.fieldsBase import maxlengthField, sizeField, StringField, SelectionWidget, finalizeFieldSchema
from Products.PloneFormGen.content.fields import FGStringField

#ATCT = Archetypes Contenttypes

from ise.pfgfieldpermission import PfgFieldPermissionMessageFactory as _

#For PROJECTNAME
from ise.pfgfieldpermission.config import PROJECTNAME 

#For Security
from AccessControl import ClassSecurityInfo


from ise.pfgfieldpermission.interfaces import IStringFieldPermission 




class FGStringFieldPermissions(BaseFormField):
    security  = ClassSecurityInfo()
    implements(IStringFieldPermission)
    
    schema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
        maxlengthField,
        sizeField,
        StringField('fgStringValidator',
            vocabulary='stringValidatorsDL',
            enforceVocabulary=1,
            widget=SelectionWidget(label=_(u'label_fgstringvalidator_text',
                                           default=u'Validator'),
                description=_(u'help_fgstringvalidator_text',
                  default=u"""Tests input against simple string patterns."""),
                ),
        ),
    ))

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FGStringFieldPermissions'
    archetype_name = 'A string field with role-based permissions'
    content_icon = 'StringField.gif'
    typeDescription= 'A string field with role-based permissions'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_string_field',
            searchable=0,
            required=0,
            write_permission = 'Modify portal content',
            read_permission = 'Modify portal content',
            validators=('isNotTooLong',),
            )


    def stringValidatorsDL(self):
        """ return a display list of string validators.
        """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getStringValidatorsDL()


    def setFgStringValidator(self, value, **kw):
        """ set simple validator """

        fgt = getToolByName(self, 'formgen_tool')

        if value and (value != 'vocabulary_none_text'):
            fgtid = fgt.stringValidators[value].get('id')
            if fgtid:
                self.fgField.validators = ('isNotTooLong', fgtid)
        else:
            self.fgField.validators = ('isNotTooLong',)
        self.fgField._validationLayer()

        self.fgStringValidator = value


atapi.registerType(FGStringFieldPermissions, PROJECTNAME)
