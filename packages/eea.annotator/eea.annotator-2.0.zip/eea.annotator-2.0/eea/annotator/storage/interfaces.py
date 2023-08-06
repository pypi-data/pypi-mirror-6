""" Storage interfaces

    >>> portal = layer['portal']
    >>> sandbox = portal['sandbox']

"""
from zope.interface import Interface
from eea.annotator.config import EEAMessageFactory as _
from zope import schema

class IAnnotatorStorage(Interface):
    """ Access/Update annotator configuration

        >>> from eea.annotator.interfaces import IAnnotatorStorage
        >>> storage = IAnnotatorStorage(sandbox)
        >>> storage
        <eea.annotator.storage.handler.Storage object...>

    """
    disabled = schema.Bool(title=_(u"Is annotator disabled?"))
    readOnly = schema.Bool(title=_(u"Is annotator read-only?"))
