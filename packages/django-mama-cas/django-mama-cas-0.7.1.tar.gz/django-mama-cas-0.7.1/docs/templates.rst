.. _templates:

Templates
=========

django-mama-cas contains templates implementing standard username and password
authentication. Depending on your needs, you can use them as-is, customize
them or replace them entirely.

.. note::

   Changes made directly to the included template files will be lost when
   django-mama-cas is updated.

**mama_cas/login.html**

   This is the main authentication form template used by ``LoginView``.
   It is displayed whenever user credentials are required. During the login
   process, it displays authentication success or failure information to the
   user. When the user logs out, by default they are redirected to this
   template, with a message indicating a successful logout.

**mama_cas/warn.html**

   This template is used by ``LoginView`` when the warn parameter from
   ``LoginFormWarn`` is in effect. This causes the login process to not be
   transparent to the user. When an authentication attempt occurs, this
   template is displayed to provide continue or cancel options for the user.

Extending
---------

The default templates provide a number of blocks for easily inserting and
modifying content. If only minor changes are required, simply extend an
existing template. Here are the basic steps:

#. Create a new template file within a templates directory of your project.
   For example, to add a header above the login form with additional styling,
   create a file with the additional content::

      {% extends "mama_cas/login.html" %}

      {% block extra_head %}
          {{ block.super }}
          <style>#header { font-size:3em; text-align:center; color:#aaa; }</style>
      {% endblock extra_head %}

      {% block header %}
          <h1>If You Can Believe Your Eyes and Ears</h1>
      {% endblock header %}

#. Make sure the template directory where this file is located is accessible
   by a `template loader`_.

#. Tell django-mama-cas to use the new template by specifying it within the
   URLconf. For example, if you are overriding the login template, it could
   look something like this::

      urlpatterns = patterns('',
          url(r'^login/?$',
          LoginView.as_view(template_name="login.html"),
          name='cas_login'),
          # ...
      )

As the final step is a bit of a hack, it is worthwhile to use something like
`django-overextends`_ to enable simultaneously overriding and extending the
stock template.

.. _template loader: https://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates
.. _django-overextends: https://github.com/stephenmcd/django-overextends

Replacing
---------

If the required changes are substantial, it may be easier to replace the stock
template entirely. If it is located in a similar path to the original template
and appears earlier in the template search order, it will be used in place of
the stock template.

In addition to the login form, some elements a custom login template should
include are:

**Messages**
   The ``messages`` framework displays information to the user for a login or
   logout event.

**Non-field errors**
   The form's ``non_field_errors`` inform the user of authentication failures
   and other login problems.
