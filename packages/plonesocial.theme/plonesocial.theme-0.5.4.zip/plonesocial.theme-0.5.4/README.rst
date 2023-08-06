Introduction
============

Plone theme based on Twitter Bootstrap 2.0.

This theme is intended to be used with the `PloneSocial suite`_.

.. _PloneSocial suite: https://github.com/cosent/plonesocial.suite


Credits
-------

|Cosent|_

Plonesocial.theme is maintained by Cosent_.

This package is forked from `diazotheme.bootstrap`_ by Izhar Firdaus.

.. _Cosent: http://cosent.nl
.. |Cosent| image:: http://cosent.nl/images/logo-external.png 
                    :alt: Cosent
.. _diazotheme.bootstrap: https://github.com/kagesenshi/diazotheme.bootstrap

Installation
============

Install the ``plonesocial.theme`` product using the Add-on Control Panel.
This will activate the theme and also setup Plone's default ``public.css``
to only included when Diazo is enabled or when you are viewing the Theming 
Control Panel. This theme includes its own ``public.css`` which had several 
items from the default ``public.css`` removed.

Features
=========

* Turn your site into a pretty Bootstrap based theme, and also simplifies
  templating of customization addons.
* Portlets are converted to ``div`` elements instead of ``dl``, ``dt``, ``dd``
* ``presentation_view`` is enhanced with Google's HTML5 slides
* Included carousel portlet provides a way to display images using Bootstrap's
  carousel
* ``eea.facetednavigation`` is also supported, with some enhancements.

  * The diazo rules rewrite facetednavigation templates to take advantage of
    the responsive design.
  * If the first widget at the top widget slot is a text search widget, it will 
    appear as a full width widget with a different background.

* Installing ``webcouturier.dropdownmenu`` will enhance the top navigation with
  dropdown menus.

Using Bootstrap javascripts
===========================

This product leaves plone jquery alone not to break existing functionality.
But bootstrap requires a newer jQuery version. We include the needed one renaming it to jQuery17.
If you need js functionality from bootstrap you have to use jQuery17, for instance

    $(function() {
        jQuery17('.tooltipped').tooltip()
    });

to activate the tooltip plugin on elements with the class "tooltipped".
