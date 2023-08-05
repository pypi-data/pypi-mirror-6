Introduction
============

The Plone_ Diazo_ based theme for Cleveland State University's Human Motion and
Control Lab, hmc.csuohio.edu_.

.. image:: img/front-page.png

.. _Plone: http://www.plone.org
.. _Diazo: http://www.diazo.org
.. _hmc.csuohio.edu: http://hmc.csuohio.edu

Installation
============

Stop Plone::

   bin/plonectl stop

Add the product to your buildout.cfg::

   eggs =
       ...
       hmc.theme

Rerun buildout::

   bin/buildout

Start Plone::

   bin/plonectl start

Log into your Plone website. In **Site Setup > Add-ons** activate Diazo
support, the ``hmc.theme``, and ``plonetheme.diazo_suburst``.
plonetheme.diazo_sunburst_ is an external dependency.

.. image:: img/add-ons.png

In **Theming > Advanced** choose the ``plonetheme.diazo_sunburst`` theme base
as the base. Note that this will remove formatting from the site setup panel
and things get jumbled up, which is a known issue.

.. image:: img/theme-base.png

Finally, in **Theming > Themes** enable the HMC theme.

.. image:: img/activate-theme.png

.. _plonetheme.diazo_sunburst: https://pypi.python.org/pypi/plonetheme.diazo_sunburst/0.0.8

Other
=====

This product may contain traces of nuts.
