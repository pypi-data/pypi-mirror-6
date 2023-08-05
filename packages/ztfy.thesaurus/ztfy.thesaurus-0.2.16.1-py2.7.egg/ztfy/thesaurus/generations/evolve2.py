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
from ztfy.thesaurus.interfaces.term import IThesaurusTerm
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility, getUtilitiesFor
from zope.location import locate
from zope.site import hooks

# import local packages
from ztfy.utils.catalog import indexObject
from ztfy.utils.catalog.index import TextIndexNG


def evolve(context):
    """Create stemm_label index in each thesaurus"""
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            intids = getUtility(IIntIds)
            for name, thesaurus in getUtilitiesFor(IThesaurus):
                catalog = thesaurus.catalog
                if 'stemm_label' not in catalog:
                    # create index
                    logger.info("Adding stemmed index in '%s' inner catalog..." % name)
                    index = TextIndexNG('label', IThesaurusTerm,
                                        field_callable=False,
                                        languages=thesaurus.language,
                                        splitter='txng.splitters.default',
                                        storage='txng.storages.term_frequencies',
                                        dedicated_storage=False,
                                        use_stopwords=True,
                                        use_normalizer=True,
                                        use_stemmer=True,
                                        ranking=True)
                    locate(index, catalog, 'stemm_label')
                    catalog['stemm_label'] = index
                    # index terms in new index
                    logger.info("Indexing terms in '%s' inner catalog..." % name)
                    for index, term in enumerate(thesaurus.terms.itervalues()):
                        indexObject(term, catalog, 'stemm_label', intids=intids)
                        if not index % 100:
                            ITransactionManager(catalog).savepoint()
