=====
Shipping
=====

Shipping is an app to use Post Office services for e-commerces built with Django.

Quick start
-----------

1. Add "shipping" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'shipping',
    )

2. Include the shipping URLconf in your project urls.py like this::

    url(r'^shipping/', include('shipping.urls')),

3. Run `python manage.py syncdb` to create the shipping models.

4. Visit http://127.0.0.1:8000/ to view a sample with a shipping service