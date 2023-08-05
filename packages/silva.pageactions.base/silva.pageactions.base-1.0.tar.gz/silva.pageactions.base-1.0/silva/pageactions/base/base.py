# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.interfaces import ISilvaObject

from silva.core.views import views as silvaviews
from five import grok

from interfaces import IPageActions, IPageAction


class PageActions(silvaviews.ViewletManager):
    """See IPageActions
    """

    grok.implements(IPageActions)
    grok.context(ISilvaObject)


class PageAction(silvaviews.Viewlet):
    """See IPageAction
    """

    grok.implements(IPageAction)
    grok.context(ISilvaObject)
    grok.viewletmanager(PageActions)
    grok.baseclass()
