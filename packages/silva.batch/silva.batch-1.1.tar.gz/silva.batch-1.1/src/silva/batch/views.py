import grokcore.component as grok

from zeam.utils.batch.views import Batching, Namespace
from zeam.utils.batch.interfaces import IBatching
from silva.core.views.traverser import UseParentByAcquisition

import Acquisition


class Zope2Batching(Batching, Acquisition.Explicit):
    grok.provides(IBatching)


class Zope2BatchTraverser(Namespace):
    """ modified traverser to support Zope2
    traversing with acquisition
    """

    def traverse(self, name, ignored):
        """ traverse through batch
        """
        super(Zope2BatchTraverser, self).traverse(name, ignored)
        return UseParentByAcquisition()


