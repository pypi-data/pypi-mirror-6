# -*- coding: utf-8 -*-

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements

from config import *

##code-section module-header #fill in your manual code here
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import relatedItemsField
from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.validation import V_REQUIRED

from plone.app.blob.subtypes.file import ExtensionBlobField
from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.field import BlobField

from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField
from plone.app.blob.mixins import ImageFieldMixin
from Acquisition import aq_base
from Products.ATContentTypes.configuration import zconf
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from zope.interface import Interface

class ITCTeaser(Interface):
    """ """

class TCExtensionImageBlobField(ExtensionField, BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """
    implements(IBlobImageField)

    def set(self, instance, value, **kwargs):
        super(TCExtensionImageBlobField, self).set(instance, value, **kwargs)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)

##/code-section module-header

schema = Schema((

    TextField('text',
      required=False,
      searchable=True,
      primary=True,
      storage = AnnotationStorage(migrate=True),
      default_output_type = 'text/html',
      widget = RichWidget(
                description = '',
                label = _(u'Text', default=u'Text'),
                rows = 25,
                allow_file_upload = False,
        ),
    ),

    StringField(
        name='external_link',
        widget=StringField._properties['widget'](
        label = _(u'External link', default=u'External link'),
        ),
    ),

    TCExtensionImageBlobField('image',
        sizes = None,
        storage = AnnotationStorage(migrate=True),
        original_size = None,
        default_content_type = 'image/png',
        allowable_content_types = ('image/gif', 'image/jpeg', 'image/png'),
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        widget = ImageWidget(
            label = _(u'label_preview_image', default=u'Preview image'),
            description=_(u''),
            show_content_type = False,
        ),
    ),

    StringField(
        name='image_caption',
        widget=StringField._properties['widget'](
        label = _(u'Image caption', default=u'Image caption'),
        ),
    ),

    BooleanField(
        name='popup',
        widget=BooleanField._properties['widget'](
            label='Open as popup',
            label_msgid='extendedlink_label_popup',
            i18n_domain='plone',
        ),
    ),
    StringField(
        name='width',
        widget=StringField._properties['widget'](
            label='Width',
            label_msgid='extendedlink_label_width',
            description='Only needed if link should be opened as popup.',
            description_msgid='extendedlink_description_width',
            i18n_domain='plone',
        ),
    ),
    StringField(
        name='height',
        widget=StringField._properties['widget'](
            label='Height',
            label_msgid='extendedlink_label_height',
            description='Only needed if link should be opened as popup.',
            description_msgid='extendedlink_description_height',
            i18n_domain='plone',
        ),
    ),
    BooleanField(
        name='blank',
        widget=BooleanField._properties['widget'](
            label='Open blank',
            label_msgid='extendedlink_label_blank',
            i18n_domain='plone',
        ),
    ),
    StringField(
        name='teaser_type',
        widget=StringField._properties['widget'](
            label='Type',
            label_msgid='extendedlink_label_type',
            description='Teaser type.',
            description_msgid='extendedlink_description_type',
            i18n_domain='plone',
        ),
    ),
))

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

##code-section after-schema #fill in your manual code here
TCTeaser_schema = ATFolder.schema.copy()+schema.copy()
TCTeaser_schema.addField(relatedItemsField.copy())
TCTeaser_schema['creation_date'].widget.visible={'edit':'visible', 'view':'invisible'}
TCTeaser_schema['relatedItems'].schemata='default'
TCTeaser_schema['relatedItems'].callStorageOnSet=True
##/code-section after-schema

class TCTeaser(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(ITCTeaser)

    meta_type = 'Teaser'
    _at_rename_after_creation = True

    schema = TCTeaser_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATFolder.__bobo_traverse__(self, REQUEST, name)

    security.declareProtected('View', 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def has_binary(self):
        """ """
        if self.getImage():
            return True

registerType(TCTeaser, PROJECTNAME)
# end of class Teaser

##code-section module-footer #fill in your manual code here
##/code-section module-footer
