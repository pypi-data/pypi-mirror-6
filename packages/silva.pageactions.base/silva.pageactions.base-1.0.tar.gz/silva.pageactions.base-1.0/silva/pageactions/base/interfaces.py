# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.views.interfaces import IViewletManager, IViewlet


class IPageActions(IViewletManager):
    """Bind page actions.
    """


class IPageAction(IViewlet):
    """An action on a page.
    """

