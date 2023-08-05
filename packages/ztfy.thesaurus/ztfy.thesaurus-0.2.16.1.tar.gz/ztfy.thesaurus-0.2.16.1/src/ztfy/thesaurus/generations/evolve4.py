### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
import logging
logger = logging.getLogger('ztfy.thesaurus')

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.component.interfaces import ISite
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility, getUtilitiesFor
from zope.site import hooks

# import local packages
from ztfy.utils.catalog import indexObject


def evolve(context):
    """Create stemm_label index in each thesaurus"""
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            intids = getUtility(IIntIds)
            for name, thesaurus in getUtilitiesFor(IThesaurus):
                # check index splitter
                logger.info("Checking index splitter in '%s' inner catalog..." % name)
                catalog = thesaurus.catalog
                for index_name in ('label', 'stemm_label'):
                    index = catalog[index_name]
                    if index._index.splitter != 'txng.splitters.default':
                        index.splitter = 'txng.splitters.default'
                        index._index.splitter = 'txng.splitters.default'
                        for count, term in enumerate(thesaurus.terms.itervalues()):
                            indexObject(term, catalog, index_name, intids=intids)
                            if not count % 100:
                                ITransactionManager(catalog).savepoint()
