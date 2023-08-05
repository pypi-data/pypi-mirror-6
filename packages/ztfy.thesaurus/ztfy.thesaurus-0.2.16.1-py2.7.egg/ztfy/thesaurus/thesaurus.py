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
from persistent import Persistent
import BTrees.Length
import re

# import Zope3 interfaces
from hurry.query.interfaces import IQuery
from transaction.interfaces import ITransactionManager
from zc.catalog.interfaces import IValueIndex
from zope.annotation.interfaces import IAnnotations
from zope.catalog.interfaces import ICatalog
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.dublincore.interfaces import IZopeDublinCore
from zope.location.interfaces import ISublocations
from zopyx.txng3.core.interfaces.ting import ITingIndex
from zopyx.txng3.core.parsers.english import QueryParserError

# import local interfaces
from ztfy.thesaurus.interfaces.loader import IThesaurusLoader
from ztfy.thesaurus.interfaces.term import IThesaurusTermsContainer, IThesaurusTerm, IThesaurusLoaderTerm
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus, \
                                                IThesaurusExtractInfo, \
                                                IThesaurusExtracts
from ztfy.thesaurus.interfaces.tree import ITree

# import Zope3 packages
from hurry.query import And, Or
from hurry.query.value import Eq
from zc.catalog.catalogindex import ValueIndex
from zope.catalog.catalog import Catalog
from zope.component import adapter, adapts, getUtility, queryUtility, getSiteManager
from zope.container.contained import Contained
from zope.container.folder import Folder
from zope.interface import implementer, implements
from zope.location.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

# import local packages
from ztfy.utils.catalog import indexObject, unindexObject
from ztfy.utils.catalog.index import TextIndexNG, Text as BaseTextSearch
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString


CUSTOM_SEARCH = re.compile(r'\*|\"|\sAND\s|\sOR\s|\sNOT\s|\(|\)', re.IGNORECASE)


class ThesaurusIndexSearch(BaseTextSearch):
    """Custom text search index using catalog instance instead of name"""

    def getIndex(self, context=None):
        if ICatalog.providedBy(self.catalog_name):
            catalog = self.catalog_name
        else:
            catalog = getUtility(ICatalog, self.catalog_name, context)
        index = catalog[self.index_name]
        assert ITingIndex.providedBy(index)
        return index


class ThesaurusValueSearch(Eq):
    """Custom value search index using catalog instance instead of name"""

    def getIndex(self, context=None):
        if ICatalog.providedBy(self.catalog_name):
            catalog = self.catalog_name
        else:
            catalog = getUtility(ICatalog, self.catalog_name, context)
        index = catalog[self.index_name]
        assert IValueIndex.providedBy(index)
        return index


class ThesaurusTermsContainer(Folder):
    """Thesaurus terms container"""

    implements(IThesaurusTermsContainer)

    def __init__(self):
        super(ThesaurusTermsContainer, self).__init__()
        self._length = BTrees.Length.Length()

    def __setitem__(self, name, term):
        if name not in self.data:
            self._length.change(1)
        term = removeSecurityProxy(term)
        self.data.__setitem__(name, term)
        locate(term, self, name)
        thesaurus = IThesaurus(self.__parent__, None)
        if thesaurus is not None:
            catalog = thesaurus.catalog
            indexObject(term, catalog)

    def __delitem__(self, name):
        term = self.data[name]
        thesaurus = IThesaurus(self.__parent__, None)
        if thesaurus is not None:
            catalog = thesaurus.catalog
            unindexObject(term, catalog)
        self.data.__delitem__(name)
        self._length.change(-1)

    def __len__(self):
        return self._length()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def iteritems(self):
        return self.data.iteritems()


class Thesaurus(Persistent, Contained):
    """Thesaurus utility"""

    implements(IThesaurus, ISublocations)

    __roles__ = ('ztfy.ThesaurusManager', 'ztfy.ThesaurusContentManager')

    name = FieldProperty(IThesaurus['name'])
    _title = FieldProperty(IThesaurus['title'])
    subject = FieldProperty(IThesaurus['subject'])
    description = FieldProperty(IThesaurus['description'])
    creator = FieldProperty(IThesaurus['creator'])
    publisher = FieldProperty(IThesaurus['publisher'])
    created = FieldProperty(IThesaurus['created'])
    language = FieldProperty(IThesaurus['language'])
    terms = None
    _top_terms = FieldProperty(IThesaurus['top_terms'])
    catalog = FieldProperty(IThesaurus['catalog'])

    administrators = RolePrincipalsProperty(IThesaurus['administrators'], role='ztfy.ThesaurusManager')
    contributors = RolePrincipalsProperty(IThesaurus['contributors'], role='ztfy.ThesaurusContentManager')

    def __init__(self, name=None, description=None, terms=None, top_terms=None):
        if name:
            self.name = name
        if terms is None:
            terms = []
        if top_terms is None:
            top_terms = []
        if description:
            self.title = description.title
            self.subject = description.subject
            self.description = description.description
            self.creator = description.creator
            self.publisher = description.publisher
            self.created = description.created
            self.language = description.language
        if not IThesaurusTermsContainer.providedBy(terms):
            terms = ThesaurusTermsContainer()
        self.terms = terms
        locate(terms, self, '++terms++')
        self.resetTermsParent()
        self.resetTopTerms()

    @property
    def title(self):
        dc = IZopeDublinCore(self, None)
        if dc is not None:
            return dc.title
        else:
            return self._title

    @title.setter
    def title(self, value):
        if value != self._title:
            self._title = value
            dc = IZopeDublinCore(self, None)
            if dc is not None:
                dc.title = value

    def sublocations(self):
        return (self.terms, self.catalog)

    @property
    def top_terms(self):
        return self._top_terms

    @top_terms.setter
    def top_terms(self, value):
        self._top_terms = [ removeSecurityProxy(term) for term in value or ()
                                                               if term.usage is None ]

    def initCatalog(self):
        catalog = self.catalog = Catalog()
        locate(catalog, self, '++catalog++')
        # init fulltext search catalog
        index = TextIndexNG('label', IThesaurusTerm,
                            field_callable=False,
                            languages=self.language,
                            splitter='txng.splitters.default',
                            storage='txng.storages.term_frequencies',
                            dedicated_storage=False,
                            use_stopwords=True,
                            use_normalizer=True,
                            ranking=True)
        locate(index, catalog, 'label')
        catalog['label'] = index
        # init stemmed search catalog
        index = TextIndexNG('label', IThesaurusTerm,
                            field_callable=False,
                            languages=self.language,
                            splitter='txng.splitters.default',
                            storage='txng.storages.term_frequencies',
                            dedicated_storage=False,
                            use_stopwords=True,
                            use_normalizer=True,
                            use_stemmer=True,
                            ranking=True)
        locate(index, catalog, 'stemm_label')
        catalog['stemm_label'] = index
        # init basic label catalog
        index = ValueIndex('base_label', IThesaurusTerm, field_callable=False)
        locate(index, catalog, 'base_label')
        catalog['base_label'] = index
        # index thesaurus terms
        locate(self.terms, self, '++terms++')
        for index, term in enumerate(self.terms.itervalues()):
            indexObject(term, catalog)
            if not index % 100:
                try:
                    ITransactionManager(catalog).savepoint()
                except TypeError:
                    # This method can fail if thesaurus is not stored yet...
                    pass

    def delete(self):
        manager = getSiteManager(self)
        manager.unregisterUtility(self, IThesaurus, self.name)
        default = manager['default']
        name = 'Thesaurus::' + self.name
        # re-parent thesaurus to site management folder
        locate(self, default, name)
        del default[name]

    def clear(self):
        self.terms.data.clear()
        self.catalog.clear()
        self.top_terms = []

    def load(self, configuration):
        loader = queryUtility(IThesaurusLoader, configuration.format)
        if loader is not None:
            result = loader.load(configuration.data)
            self.merge(configuration, result)

    def merge(self, configuration, thesaurus=None):
        if thesaurus is None:
            loader = queryUtility(IThesaurusLoader, configuration.format)
            if loader is not None:
                thesaurus = loader.load(configuration.data)
        if thesaurus is not None:
            # define or merge items from given thesaurus
            terms = self.terms
            for index, (key, term) in enumerate(thesaurus.terms.iteritems()):
                # check for term conflict
                if configuration.conflict_suffix:
                    suffixed_key = key + ' ' + configuration.conflict_suffix
                    if suffixed_key in terms:
                        key = suffixed_key
                    elif key in terms:
                        term.label = key
                if key in terms:
                    terms[key].merge(term, configuration)
                elif not IThesaurusLoaderTerm.providedBy(term):
                    terms[key] = term
                if not index % 100:
                    try:
                        ITransactionManager(self).savepoint()
                    except TypeError:
                        # This method can fail if thesaurus is not stored yet...
                        pass
        self.resetTermsParent()
        self.resetTopTerms()

    def resetTermsParent(self):
        for index, term in enumerate(self.terms.itervalues()):
            # reset generic/specifics attributes
            generic = term.generic
            if (generic is not None) and (term not in generic.specifics):
                generic.specifics = generic.specifics + [term, ]
            # reset term's first level parent
            parent = term
            while parent.generic is not None:
                parent = parent.generic
            term.parent = parent
            if not index % 100:
                try:
                    ITransactionManager(self).savepoint()
                except TypeError:
                    # This method can fail if thesaurus is not stored yet...
                    pass

    def resetTopTerms(self):
        self.top_terms = [term for term in self.terms.itervalues()
                          if (not term.generic) and (not term.usage)]

    def findTerms(self, query=None, extract=None, autoexpand='always', glob='end', limit=None,
                  exact=False, exact_only=False, stemmed=False):
        assert exact or (not exact_only)
        query_util = getUtility(IQuery)
        terms = []
        if exact:
            search = ThesaurusValueSearch((self.catalog, 'base_label'),
                                          translateString(query, escapeSlashes=True, forceLower=True, spaces=' '))
            terms = list(query_util.searchResults(search))
        if not exact_only:
            searches = []
            # check stemmed index
            if stemmed and not re.search(r'\*', query):
                index = (self.catalog, 'stemm_label')
                searches.append(ThesaurusIndexSearch(index, {'query': u' '.join(m for m in query.split() if len(m) > 2),
                                                             'autoexpand': 'off',
                                                             'ranking': False}))
            # check basic index
            start = ''
            end = ''
            if CUSTOM_SEARCH.search(query):
                query_text = query
                autoexpand = 'off'
            else:
                if glob in ('start', 'both'):
                    start = u'*'
                if glob in ('end', 'both'):
                    end = u'*'
                query_text = u' '.join((u'%s%s%s' % (start, m, end) for m in query.split() if len(m) > 2))
            index = (self.catalog, 'label')
            searches.append(ThesaurusIndexSearch(index, {'query': query_text,
                                                         'autoexpand': autoexpand,
                                                         'ranking': False}))
            try:
                terms += sorted(query_util.searchResults(Or(*searches), limit=limit), key=lambda x: x.label)
            except QueryParserError:
                pass
        if extract:
            terms = [term for term in terms if extract in term.extracts]
        return terms


@adapter(IThesaurus, IObjectAddedEvent)
def handleNewThesaurus(thesaurus, event):
    """Handle new thesaurus"""
    thesaurus.initCatalog()


class ThesaurusTreeAdapter(object):
    """Thesaurus tree adapter"""

    adapts(IThesaurus)
    implements(ITree)

    def __init__(self, context):
        self.context = context

    def getRootNodes(self):
        return self.context.top_terms


#
# Thesaurus extracts
#

class ThesaurusExtract(Persistent, Contained):
    """Thesaurus extract"""

    implements(IThesaurusExtractInfo)

    __roles__ = ('ztfy.ThesaurusExtractManager',)

    name = FieldProperty(IThesaurusExtractInfo['name'])
    description = FieldProperty(IThesaurusExtractInfo['description'])
    abbreviation = FieldProperty(IThesaurusExtractInfo['abbreviation'])
    color = FieldProperty(IThesaurusExtractInfo['color'])

    managers = RolePrincipalsProperty(IThesaurusExtractInfo['managers'], role='ztfy.ThesaurusExtractManager')

    def addTerm(self, term):
        term.addExtract(self)

    def removeTerm(self, term):
        term.removeExtract(self)


@adapter(IThesaurusExtractInfo, IObjectRemovedEvent)
def handleRemovedExtractInfo(extract, event):
    thesaurus = getParent(extract, IThesaurus)
    name = getName(extract)
    for term in thesaurus.terms:
        term.removeExtract(name, check=False)


class ThesaurusExtractsContainer(Folder):
    """Thesaurus extracts container"""

    implements(IThesaurusExtracts)


THESAURUS_EXTRACTS_KEY = 'ztfy.thesaurus.extracts'

@adapter(IThesaurus)
@implementer(IThesaurusExtracts)
def ThesaurusExtractsFactory(context):
    """Thesaurus extracts adapter"""
    annotations = IAnnotations(context)
    extracts = annotations.get(THESAURUS_EXTRACTS_KEY)
    if extracts is None:
        extracts = annotations[THESAURUS_EXTRACTS_KEY] = ThesaurusExtractsContainer()
        locate(extracts, context, '++extracts++')
    return extracts
