==========================
django-simple-blog
==========================

What is it?
===========

django-simple-blog is a simple Django app for fast integrating your
current project with a blog-system 

You can easily write blog posts, let users comment the posts if you'd like to.

Installation
============

You can do any of the following to install ``django-simple-blog``

- Run ``pip install django-simple-blog``.
- Run ``easy_install django-simple-blog``.
- Download or "git clone" the package and run ``setup.py``.
- Download or "git clone" the package and add ``simpleblog`` to your PYTHONPATH.


Usage
=====

1. Add ``simpleblog`` to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'simpleblog',
      )
2. Run ``syncdb``
3. Include the ``simpleblog urls`` like this to have your "home page" as the blog index::

	...
	from simpleblog.views import BlogListView
	...

      urlpatterns = patterns('',
          url(r'^$', BlogListView.as_view(), name='home'),
          url(r'^blog/', include('simpleblog.urls')),
          url(r'^admin/', include(admin.site.urls)),
      )

Settings
========
``django-simple-blog`` has one setting at the moment::

  # How long the length of the textarea should be.
  
  MAX_LENGTH_TEXTAREA = 120 (defaults to None)


Templatetags
===========

``django-simple-blog`` comes with one templatetag for getting
the latest desired number of posts. Just do this in any template::
  {% load blog_tags %}
  
  {% latest_blog_posts 5 %}


Translation
===========

``django-simple-blog`` is available in ``english`` and ``swedish``
at the moment, feel free to translate the application in another
language.

Admin
=====
For writing posts we will use django's admin application.

The templates
=============

The templates is just there as examples for how your templates
could look like, but they work excellent as well, but if you don't
like them, just override them with your own templates simply.

Requirements
============

`Django>=1.5
<https://github.com/django/django/>`_

`endless-pagination>=2.0
<https://github.com/frankban/django-endless-pagination/>`_

`simplemathcaptcha>=1.0.2
<https://github.com/alsoicode/django-simple-math-captcha/>`_

If you have problem getting the right versions of these packages,
clone them from their github repository.