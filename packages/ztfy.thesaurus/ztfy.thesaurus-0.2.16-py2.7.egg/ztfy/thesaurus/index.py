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

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.thesaurus.interfaces.index import IThesaurusTermFieldIndex, IThesaurusTermsListFieldIndex

# import Zope3 packages
from zc.catalog.catalogindex import SetIndex
from zc.catalog.index import SetIndex as SetIndexBase
from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


def getIndexTerms(index, term):
    terms = [term, ]
    if index.include_parents:
        terms.extend(term.getParents())
    if index.include_synonyms:
        if term.usage is not None:
            terms.append(term.usage)
        else:
            terms.extend(term.used_for)
    print ', '.join(term.label for term in terms)
    return terms


class ThesaurusTermFieldIndex(SetIndex):
    """Thesaurus term field index"""

    implements(IThesaurusTermFieldIndex)

    include_parents = FieldProperty(IThesaurusTermFieldIndex['include_parents'])
    include_synonyms = FieldProperty(IThesaurusTermFieldIndex['include_synonyms'])

    def index_doc(self, docid, object):
        if self.interface is not None:
            object = self.interface(object, None)
            if object is None:
                return None
        value = getattr(object, self.field_name, None)
        if value is not None and self.field_callable:
            value = value()

        if not value:
            self.unindex_doc(docid)
            return None

        intids = getUtility(IIntIds)
        value = [intids.register(term) for term in set(getIndexTerms(self, value))]
        return SetIndexBase.index_doc(self, docid, value)


class ThesaurusTermsListFieldIndex(SetIndex):
    """Thesaurus terms list field index"""

    implements(IThesaurusTermsListFieldIndex)

    include_parents = FieldProperty(IThesaurusTermsListFieldIndex['include_parents'])
    include_synonyms = FieldProperty(IThesaurusTermsListFieldIndex['include_synonyms'])

    def index_doc(self, docid, object):
        if self.interface is not None:
            object = self.interface(object, None)
            if object is None:
                return None
        value = getattr(object, self.field_name, None)
        if value is not None and self.field_callable:
            value = value()

        if not value:
            self.unindex_doc(docid)
            return None

        terms = []
        [terms.extend(getIndexTerms(self, term)) for term in value]

        intids = getUtility(IIntIds)
        value = [intids.register(term) for term in set(terms)]
        return SetIndexBase.index_doc(self, docid, value)
