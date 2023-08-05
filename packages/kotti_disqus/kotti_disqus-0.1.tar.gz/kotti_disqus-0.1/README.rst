============
kotti_disqus
============

This is an extension to the Kotti CMS that adds a commenting system to your
site. It uses `Disqus <http://disqus.com/>`_, so you need to register an
account there before you can use it.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_disqus`` add-on in your Kotti site, you need to add an
entry to the ``kotti.configurators`` setting in your Paste Deploy config. If
you don't have a ``kotti.configurators`` option, add one. ``kotti_disqus``
depends on ``kotti_settings`` so you need to add a line for this add-on too::

    kotti.configurators =
        kotti_settings.kotti_configure
        kotti_disqus.kotti_configure

You can change some settings at the settings page
(http://your.domain/@@settings or use the submenu of "Site Setup").

+------------------------+----------------------------------------------------+
| Option                 | Explanation                                        |
+========================+====================================================+
| Disqus Shortname       | The shortname you registered at Disqus.            |
|                        | **Necessary for the commenting system to work!**   |
+------------------------+----------------------------------------------------+
| Disqus Base URL        | Change the base URL - useful if you move your site |
|                        | to another URL but want to keep your comments.     |
|                        | Will use the current URL if not set.               |
+------------------------+----------------------------------------------------+
| Disqus Available Types | Select the types on which you want to enable       |
|                        | comments. You can select from all types available  |
|                        | to Kotti via ``kotti.available_types``. **If       |
|                        | nothing is selected, comments won't appear so be   |
|                        | sure to select at least one of these.**            |
+------------------------+----------------------------------------------------+

If you need to include a type not available in ``kotti.available_types`` or
want to force an option that can never be disabled, you can do so via
``kotti_disqus.extra_types``, such as::

  kotti_disqus.extra_types =
      kotti.resources.Document
      kotti.resources.Image


.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
