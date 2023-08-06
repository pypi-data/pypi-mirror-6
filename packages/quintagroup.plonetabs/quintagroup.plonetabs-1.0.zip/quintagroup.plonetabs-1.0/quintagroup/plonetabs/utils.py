""" This module dedicated to work with viewlets. """
from Acquisition import aq_inner

from plone.app.customerize import registration

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewlet


# TODO: Methods 'getViewletByName' and 'setupViewletByName' were copied from
# https://github.com/collective/collective.developermanual/blob/master/source/
#                                 views/viewlets.rst#rendering-viewlet-by-name
# Better solution would be to use collective.fastview
# (http://svn.plone.org/svn/collective/collective.fastview/trunk/)
# which has not yet included in plone.

def getViewletByName(name):
    """ Viewlets allow through-the-web customizations.

    Through-the-web customization magic is managed by five.customerize.
    We need to think of this when looking up viewlets.

    @return: Viewlet registration object
    """
    views = registration.getViews(IBrowserRequest)

    for v in views:

        if v.provided == IViewlet:
            # Note that we might have conflicting BrowserView with the
            # same name, thus we need to check for provided
            if v.name == name:
                return v

    return None


def setupViewletByName(view, context, request, name):
    """ Constructs a viewlet instance by its name.

    Viewlet update() and render() method are not called.

    @return: Viewlet instance of None if viewlet with name does not exist
    """
    context = aq_inner(context)

    # Perform viewlet regisration look-up
    # from adapters registry
    reg = getViewletByName(name)
    if reg is None:
        return None

    # factory method is responsible for creating the viewlet instance
    factory = reg.factory

    # Create viewlet and put it to the acquisition chain
    # Viewlet need initialization parameters: context, request, view
    try:
        viewlet = factory(context, request, view, None).__of__(context)
    except TypeError:
        # Bad constructor call parameters
        raise RuntimeError("Unable to initialize viewlet %s. Factory "
                           "method %s call failed." % (name, str(factory)))

    return viewlet
