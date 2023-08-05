from bise.catalogueindexer.adapters.basic import PACDocumentCataloguer
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import cgi


class FactsheetCataloguer(PACDocumentCataloguer):

    def get_values_to_index(self):
        request = getRequest()
        items = super(FactsheetCataloguer, self).get_values_to_index()
        view = getMultiAdapter((self.context, request), name='view')
        contents = u''
        for item in view.facts():
            for fact in item.get('facts'):
                contents += getMultiAdapter(
                    (fact.getObject(), request),
                    name='factrenderview')()

        items['article[content]'] = cgi.escape(contents)

        return items
