""" Control Panel Interfaces

   >>> portal = layer['portal']
   >>> sandbox = portal['sandbox']

"""
from zope.interface import Interface
from zope import schema
from eea.annotator.config import EEAMessageFactory as _

class ISettings(Interface):
    """ Settings

        >>> from eea.annotator.interfaces import ISettings
        >>> ISettings(portal).portalTypes = [u'Document', u'News Item']
        >>> ISettings(portal).portalTypes
        [u'Document', u'News Item']

    """
    portalTypes = schema.List(
        title=_(u"Enable inline comments"),
        description=_(u"Annotator inline comments are enabled for the "
                      u"following content-types"),
        required=False,
        default=[u"Document"],
        value_type=schema.Choice(
            vocabulary=u"plone.app.vocabularies.ReallyUserFriendlyTypes")
    )

    autoSync = schema.Int(
        title=_(u"Auto-refresh inline comments"),
        description=_(
            u"Define the auto-refresh interval in seconds of inline comments "
            u"within a page. Minimum recommended 30 seconds. "
            u"Use 0 to disable auto-refresh."
        ),
        required=False,
        default=0
    )
