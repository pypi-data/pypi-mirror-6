""" Storage
"""
import json
import hashlib
from datetime import datetime
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from eea.annotator.interfaces import IAnnotatorStorage
from Products.CMFCore.utils import getToolByName
from eea.annotator.config import PROJECTNAME
from persistent.dict import PersistentDict
from eea.annotator.config import EEAMessageFactory as _

class Storage(object):
    """ Annotator storage adapter
    """
    implements(IAnnotatorStorage)

    def __init__(self, context):
        self.context = context

    @property
    def _storage(self):
        """ Editable storage
        """
        anno = IAnnotations(self.context)
        storage = anno.get(PROJECTNAME, None)
        if not storage:
            storage = anno[PROJECTNAME] = PersistentDict()
        return storage

    @property
    def storage(self):
        """ Read-only storage
        """
        anno = IAnnotations(self.context)
        return anno.get(PROJECTNAME, {})

    @property
    def _comments(self):
        """ Editable comments
        """
        comments = self._storage.get('comments')
        if not comments:
            comments = self._storage['comments'] = PersistentDict()
        return comments

    @property
    def user(self):
        """ Current user
        """
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        name = member.getId()
        title = member.getProperty('fullname', name) or name

        return {
            'id': name,
            'name': title
        }

    @property
    def date(self):
        """ Current date
        """
        now = datetime.utcnow()
        return now.isoformat()

    @property
    def comments(self):
        """ Read-only comments
        """
        return self.storage.get('comments', {})

    #
    # Public interface
    #
    @property
    def disabled(self):
        """ Annotator disabled?
        """
        return getattr(self.context, 'disableAnnotator', False)

    @disabled.setter
    def disabled(self, value):
        """ Disable inline comments
        """
        setattr(self.context, 'disableAnnotator', value)

    @property
    def readOnly(self):
        """ Read-only inline comments
        """
        return getattr(self.context, 'readOnlyAnnotator', False)

    @readOnly.setter
    def readOnly(self, value):
        """ Make inline comments read-only
        """
        setattr(self.context, 'readOnlyAnnotator', value)
    #
    # Inline comments
    #
    def get(self, name, default=None):
        """ Get item by name
        """
        return self.comments.get(name, default)

    def add(self, comment):
        """ Add inline comment
        """
        if isinstance(comment, str):
            comment = comment.decode('utf-8')

        oid = hashlib.md5(comment.encode('utf-8')
            if isinstance(comment, unicode) else repr(comment)).hexdigest()
        if isinstance(comment, unicode):
            comment = json.loads(comment)

        comment['id'] = oid
        comment['created'] = comment['updated'] = self.date
        comment['user'] = self.user

        self._comments[oid] = PersistentDict(comment)
        return comment

    def replies(self, comment):
        """ Handle replies to comment
        """
        cid = comment.get('id')
        oldComment = self.comments.get(cid, {})
        oldReplies = oldComment.get('replies', [])
        replies = comment.get('replies', [])

        for reply in replies:
            # Delete
            if reply.pop('remove', False):
                text = reply.get('reply', '')
                oldReplies = [r for r in oldReplies if r.get('reply') != text]
            # Create
            elif not reply.get('user'):
                reply['user'] = self.user
                reply['created'] = self.date
                oldReplies.append(reply)

        comment['replies'] = oldReplies
        return comment

    def edit(self, comment, delete=False):
        """ Update existing comment
        """
        if isinstance(comment, str):
            comment = comment.decode('utf-8')
        if isinstance(comment, unicode):
            comment = json.loads(comment)

        comment['updated'] = self.date

        # Preserve history for comment's close/reopen
        if delete:
            reply = {}
            deleted = comment.get('deleted', False)
            if deleted:
                reply['reply'] = _('Comment closed').decode('utf-8')
            else:
                reply['reply'] = _('Comment reopened').decode('utf-8')
            comment.setdefault('replies', [])
            comment['replies'].append(reply)

        comment = self.replies(comment)

        oid = comment.get('id')
        self._comments[oid] = PersistentDict(comment)
        return comment

    def delete(self, comment):
        """ Delete comment
        """
        if isinstance(comment, str):
            comment = comment.decode('utf-8')
        if isinstance(comment, unicode):
            comment = json.loads(comment)

        oid = comment.get('id')
        if not oid or oid not in self.comments:
            return

        # History enabled
        if comment.get('deleted', None) is not None:
            return self.edit(comment, delete=True)

        return self._comments.pop(oid)
