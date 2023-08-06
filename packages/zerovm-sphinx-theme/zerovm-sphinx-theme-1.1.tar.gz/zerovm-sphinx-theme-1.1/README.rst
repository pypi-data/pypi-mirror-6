ZeroVM Theme for Sphinx
=======================

This package bundles the ZeroVM_ theme for Sphinx_.

Install the package and add this to your ``conf.py``::

    import zerovm_sphinx_theme
    html_theme_path = [zerovm_sphinx_theme.theme_path]
    html_theme = 'zerovm'

That will configure the theme path correctly and activate the theme.

Changelog
---------

1.1 (2014-03-28):
    Version 1.0 did not work since ``README.rst`` wasn't distributed.

1.0 (2014-03-28):
    First release.

.. _zerovm: http://zerovm.org/
.. _sphinx: http://sphinx-doc.org/
