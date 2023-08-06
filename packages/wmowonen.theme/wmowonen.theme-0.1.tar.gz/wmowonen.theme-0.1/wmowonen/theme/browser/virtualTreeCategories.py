from Products.Five import BrowserView
from collective.virtualtreecategories.interfaces import \
    IVirtualTreeCategoryConfiguration
from plone.i18n.normalizer import IDNormalizer
from zope.component.hooks import getSite


class VirtualTreeCategoryView(BrowserView):

    def tag(self, keywords):
        keywords = self.matched_keywords(keywords)
        if keywords:
            keyword = keywords[0]
            return {'id': IDNormalizer().normalize(keyword),
                    'title': keyword}

    def matched_keywords(self, keywords):
        """Return the first keyword that belongs to the 'kies-een-thema'
        category in the VirtualTreeCategory configuration.
        """
        site = getSite()
        treeconf = IVirtualTreeCategoryConfiguration(site)
        categories = [cat for cat in treeconf.list_categories('/')
                      if cat.id == 'kies-een-thema']
        if not categories:
            return None
        category = categories[0]
        matched_keywords = list(set(category.keywords).intersection(
            set(keywords)))
        return matched_keywords
