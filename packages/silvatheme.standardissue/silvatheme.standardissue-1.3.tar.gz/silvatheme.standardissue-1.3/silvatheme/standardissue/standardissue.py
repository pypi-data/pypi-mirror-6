from zope.cachedescriptors.property import CachedProperty
from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf
from silva.core.layout.porto import porto
from silva.core.layout.porto.interfaces import IPorto
from silva.core.interfaces import IPublication


class IStandardIssue(IPorto):
    """Layer for standard issue theme
    """

    silvaconf.resource('default.css')


class IStandardIssueSkin(IStandardIssue, ISilvaSkin):
    """Skin for standard issue theme
    """

    silvaconf.skin('Standard Issue')


silvaconf.layer(IStandardIssue)

class Navigation(porto.Navigation):
    max_depth = 1


class Layout(porto.Layout):

    @CachedProperty
    def publication_title(self):
        return self.context.get_publication().get_title()

    @CachedProperty
    def publication_url(self):
        return self.context.get_publication().absolute_url()

    def top_menu_items(self):
        root = self.context.get_root()
        def publishable(x):
            return x.is_published() and IPublication.providedBy(x)
        return filter(publishable, root.get_ordered_publishables())

    def current_publication_class(self, publication):
        if publication in self.request.PARENTS:
            return 'active'
        return ''

    def current_navigation_title(self):
        return self.context.get_publication().get_title()


class Favicon(porto.Favicon):
    """Declare that we have a favicon for this layer.

    Default favicon url is static/favicon.ico so we don't need to
    do anything besides declaring the Favicon viewlet inside this
    layer and have a static/favicon.ico file.
    If you want it to be something different, define a favicon_url property
    or method for this class.
    """
    pass
