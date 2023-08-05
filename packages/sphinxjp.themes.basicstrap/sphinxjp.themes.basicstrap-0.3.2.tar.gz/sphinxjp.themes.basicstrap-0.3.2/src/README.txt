Basicstrap style theme for Sphinx. Using Twitter Bootstrap.

.. image:: https://drone.io/github.com/tell-k/sphinxjp.themes.basicstrap/status.png
   :target: https://drone.io/github.com/tell-k/sphinxjp.themes.basicstrap

Features
========
* Provide ``basicstrap`` theme for render HTML document.
* Using `Twitter Bootstrap <http://twitter.github.com/bootstrap/>`_.
* Support Responsive Design.
* Change the layout flexibility.
* `Google Web Fonts <http://www.google.com/webfonts>`_ available.
* `Font Awesome <http://fortawesome.github.com/Font-Awesome/>`_ available.
* Easily change the design. by `Bootswatch <http://bootswatch.com/>`_.


Set up
======
Make environment with pip::

    $ pip install sphinxjp.themes.basicstrap

Make environment with easy_install::

    $ easy_install sphinxjp.themes.basicstrap


Convert Usage
=============
setup conf.py with::

    extensions += ['sphinxjp.themes.basicstrap']
    html_theme = 'basicstrap'

and run::

    $ make html

.. caution:: Caution when upgrading from 0.1.1 to 0.2.0

 * In version 0.1.1, the header color was black in the default, it has become white in 0.2.0. 
 * If you like the black color header, please set to True the 'header_inverse' option. 

Requirement
===========
* Python 2.7 or later.
* Sphinx 1.2.x or later.

Using
===========
* Twitter Bootstrap 2.3.2
* jQuery 1.8.3
* Bootswatch
* Font Awesome 3.2.1

License
=======

* sphinxjp.themes.basicstrap Licensed under the `MIT license <http://www.opensource.org/licenses/mit-license.php>`_ .
* `Twitter Bootstrap is licensed under the Apache license <https://github.com/twitter/bootstrap/blob/master/LICENSE>`_.
* `Bootswatch is licensed under the Apache license <https://github.com/thomaspark/bootswatch/blob/gh-pages/LICENSE>`_.
* `Font Awesome is licensed under the license <https://github.com/FortAwesome/Font-Awesome>`_.
* `Geo is licensed under the license <https://github.com/divshot/geo-bootstrap>`_

See the LICENSE file for specific terms.
