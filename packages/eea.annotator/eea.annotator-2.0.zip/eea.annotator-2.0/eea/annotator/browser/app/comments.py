""" Inline comments
"""
import json
from datetime import datetime
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from eea.annotator.interfaces import IAnnotatorStorage


class InlineComments(BrowserView):
    """ Display all inline comments
    """
    def jsonify(self, obj):
        """ JSON
        """
        return json.dumps(dict(obj))

    @property
    def comments(self):
        """ All comments sorted by date
        """
        def compare(a, b):
            """ Custom sorting cmp
            """
            a_up = datetime.strptime(a.get('updated'), "%Y-%m-%dT%H:%M:%S.%f")
            b_up = datetime.strptime(b.get('updated'), "%Y-%m-%dT%H:%M:%S.%f")
            return cmp(b_up, a_up)

        storage = queryAdapter(self.context, IAnnotatorStorage)
        for comment in sorted(storage.comments.values(), cmp=compare):
            yield comment
