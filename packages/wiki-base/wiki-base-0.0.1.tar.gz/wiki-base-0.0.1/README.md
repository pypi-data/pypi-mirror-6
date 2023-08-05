django-wiki-base
================

Background
----------

Django-wiki-base is a lightweight, stripped down version of [django-wiki](https://github.com/benjaoming/django-wiki), it only contains structure models (to be easily included in existing project via API).

Current goals
-------------

* Strip all unneeded stuff - views, etc.
* Transform Article to use "block system" (think MediaWiki) from which article menu could be created
* Markdown optional (there isn't any useable WYSIWYG Markdown editor)

Changes from django-wiki
------------------------

* Moved ArticleRevision `deleted` and `locked` flags to Article

Contributing
------------

If you have a great idea, let me know; for now I'd like to keep everything as simple as possible.

Dependencies
------------

So far the dependencies are:

 * [django>=1.4](http://www.djangoproject.com)
 * [django-south](http://south.aeracode.org/)
 * [Markdown>=2.2.0](https://github.com/waylan/Python-Markdown)
 * [django-mptt>=0.5.3](https://github.com/django-mptt/django-mptt)
 * [django-sekizai](https://github.com/ojii/django-sekizai/)
 * [sorl-thumbnail](https://github.com/sorl/sorl-thumbnail) (to be removed?)
 * Pillow (Python Imaging Library)
 * Python>=2.5<3 (Python 3 not yet supported)

Development
------------

In your Git fork, run `pip install -r requirements.txt` to install the requirements.

The folder **testproject/** contains a pre-configured django project (subject to change) and an sqlite database. Login for django admin is *admin:admin*. This project should always be maintained, but please do not commit changes to the SQLite database as we only care about its contents in case data models are changed.


Python 2.5
----------

It's compatible and being run on a server with Python 2.5.

Due to Markdown using elementree, you should check that you have python-celementtree: `apt-get install python-celementtree`

Acknowledgements
----------------

 * [Original wiki maintainers](https://github.com/benjaoming/django-wiki/graphs/contributors)
 * The people at [edX](http://www.edxonline.org/) & MIT for finding and supporting the project both financially and with ideas.
 * [django-cms](https://github.com/divio/django-cms) for venturing where no django app has gone before in terms of well-planned features and high standards. It's a very big inspiration.
 * [django-mptt](https://github.com/django-mptt/django-mptt), a wonderful utility for inexpensively using tree structures in Django with a relational database backend.
 * [jdcaballero](https://github.com/jdcaballero), [yekibud](https://github.com/yekibud), [bridger](https://github.com/bridger), [TomLottermann](https://github.com/TomLottermann), [crazyzubr](https://github.com/crazyzubr), and [everyone else](https://github.com/benjaoming/django-wiki/contributors) involved!

<!---Illegal PyPi RST data -->
<!---Anything that isn't validly translateable to PyPi RST goes after this line -->

