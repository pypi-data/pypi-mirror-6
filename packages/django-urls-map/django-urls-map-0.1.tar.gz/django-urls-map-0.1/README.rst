This is a simple Django app to embed a management command that will display the urls map of your project.

The urls map is an agregated list of urls from all installed apps in your settings.

Install
=======

Add it to your installed apps in the settings : ::

    INSTALLED_APPS = (
        ...
        'django_urls_map',
        ...
    )

Usage
=====

To display the full url list, just do : ::

    ./manage.py urlmap

Note that this will include also all the Django admin urls if enabled, it's a little verbose.

So if needed you can exclude some paths, like for the Django admin : ::

    ./manage.py urlmap --exclude="/admin/"

And this will render something like that (depends on what apps you have installed) : ::
    
    * /media/(?P<path>.*) Unnamed
    * /
    * /static\/(?P<path>.*) Unnamed
    * /slideshows/
    * /slideshows/show_slides/(?P<slug>[-\w]+)/ show_slides
    * /slideshows/random_slide/(?P<slug>[-\w]+)/ random_slide
    * /ckeditor/editor_site_templates.js ckeditor-editor-site-templates
    * /admin_tools/
    * /admin_tools/menu/
        * /admin_tools/menu/add_bookmark/ admin-tools-menu-add-bookmark
        * /admin_tools/menu/edit_bookmark/(?P<id>.+)/ admin-tools-menu-edit-bookmark
        * /admin_tools/menu/remove_bookmark/(?P<id>.+)/ admin-tools-menu-remove-bookmark
    * /admin_tools/dashboard/
        * /admin_tools/dashboard/set_preferences/(?P<dashboard_id>.+)/ admin-tools-dashboard-set-preferences
    * /accounts/
    * /accounts/activate/complete/ registration_activation_complete
    * /accounts/activate/(?P<activation_key>\w+)/ registration_activate
    * /accounts/register/ registration_register
    * /accounts/register/complete/ registration_complete
    * /accounts/register/closed/ registration_disallowed
    * /accounts/login/ auth_login
    * /accounts/password/change/ auth_password_change
    * /accounts/password/reset/ auth_password_reset
    * /accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/ auth_password_reset_confirm
    * /accounts/
        * /accounts/login/ auth_login
        * /accounts/logout/ auth_logout
        * /accounts/password/change/ auth_password_change
        * /accounts/password/change/done/ auth_password_change_done
        * /accounts/password/reset/ auth_password_reset
        * /accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/ auth_password_reset_confirm
        * /accounts/password/reset/complete/ auth_password_reset_complete
        * /accounts/password/reset/done/ auth_password_reset_done
    * /en-us/
    * /en-us/
        * /en-us/ pages-root
        * /en-us/(?P<slug>[0-9A-Za-z-_.//]+)/ pages-details-by-slug

This sample was generated from a Django project that includes "Django cms", "Django admin tools", "emencia-django-slideshows
" and a custom app based on "Django registration". Note that the render uses colored terminal output (to assure some readability).

You can many path to exclude, the paths is raw strings (not Regex) and are only used with the "startswith" method, this means it will only match your paths from the start of urls.
