mezzanine-slides
================

Add simple slide functionality to your Mezzanine based website allowing for
beautiful banners at the tops of pages.


Setup
-----

1. Run ``pip install mezzanine-slides``
2. In ``settings.py`` add ``mezzanine_slides`` to your ``INSTALLED_APPS`` above
   mezzanine apps.
3. Run createdb or syncdb, if running syncdb run migrate if you are using South.
4. If you haven't modified your ``base.html`` or ``pages/page.html`` templates
   then you can just ``manage.py collecttemplates mezzanine_slides`` and use the
   ones I provide. If you've already modified these templates see the Templates
   section for continued instruction.


Templates
---------

Add this to your ``pages/page.html`` anywhere as long as it's not inside another
block::

  {% block slides %}{% include "includes/slides.html" %}{% endblock %}

Add this to ``base.html`` where you would like the slides to appear, which is
usually between your main content and the navigation::

  {% block slides %}{% endblock %}

Now you'll need to include the CSS and JS in your compress areas of your
``base.html`` template::

  {% compress css %}
  ...
  <link rel="stylesheet" href="{% static "css/responsiveslides.css" %}">
  {% endcompress %}

  
  {% compress js %}
  ...
  <script src="{% static "js/responsiveslides.min.js" %}"></script>
  <script src="{% static "js/responsiveslides-init.js" %}"></script>
  {% endcompress %}


Credits
-------

Thanks to `Viljami Salminen`_ for his great `ResponsiveSlides.js`_ plugin.


.. Links

.. _Viljami Salminen: http://viljamis.com/
.. _ResponsiveSlides.js: http://responsive-slides.viljamis.com/

