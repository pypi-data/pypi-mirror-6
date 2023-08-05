django-wiki-base
================

Background
----------

Django-wiki-base is a lightweight, stripped down version of [django-wiki](https://github.com/benjaoming/django-wiki), it only contains structure models (to be easily included in existing project via API).

Current goals
-------------

* Markup language switch (Markdown, reST, HTML, ..)

Changes from django-wiki
------------------------

* Moved ArticleRevision `deleted` and `locked` flags to Article
* Strip all unneeded stuff - views, etc.
* Transform Article to use Sections' (based on MPTT - possible to reorder/nest) from which article menu could be created (think MediaWiki)

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
 * [sorl-thumbnail](https://github.com/sorl/sorl-thumbnail) (to be removed?)
 * Pillow (Python Imaging Library)
 * Python>=2.5<3 (Python 3 not yet supported)

Development
------------

In your Git fork, run `pip install -r requirements.txt` to install the requirements.

The folder **testproject/** contains a pre-configured django project (subject to change) and an sqlite database. Login for django admin is *admin:admin*. This project should always be maintained, but please do not commit changes to the SQLite database as we only care about its contents in case data models are changed.


Python compatibility
--------------------

It was compatible with Python 2.5 when I cloned from django-wiki repository (Jan 2014), but I'm developing on 2.7.
Feel free to contact me/send a pull request if something has broken (not related to plugins).

Due to Markdown using elementree, you should check that you have python-celementtree: `apt-get install python-celementtree`

Acknowledgements
----------------

 * [Original wiki developers and maintainers](https://github.com/benjaoming/django-wiki/graphs/contributors)

<!---Illegal PyPi RST data -->
<!---Anything that isn't validly translateable to PyPi RST goes after this line -->

