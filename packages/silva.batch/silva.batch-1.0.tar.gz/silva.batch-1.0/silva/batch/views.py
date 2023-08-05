import grokcore.component as grok

from zeam.utils.batch.views import Batching
from zeam.utils.batch.interfaces import IBatching

import Acquisition


class Zope2Batching(Batching, Acquisition.Explicit):
    grok.provides(IBatching)
