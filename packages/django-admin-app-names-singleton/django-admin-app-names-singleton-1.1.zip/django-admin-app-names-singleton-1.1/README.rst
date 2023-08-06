=====
Translate app names and allow singletons
=====

This is a simple Django app to enable translation of app names in
Django admin and allow the use of singletons.
When an object is marked as a singleton only one instance will be allowed to exist.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1.  Add "django_singleton_app_name" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'django_singleton_app_name',
      )

      
2.  Copy templates from django-admin-app-names-singleton/templates
    to your project's template directory.
    All app names will now be translated when possible.
    In order to add app names to .po files via "makemessages"
    create a python file "app_names.py" next to your "settings.py" file
    and paste the following import into it:
    "from django.utils.translation import ugettext_lazy as _".
    For each app you want to mark for translation add a line such as the following:
    _("<app_name>")
    Example:
    _("auth")

    
3.  To mark a model as a singleton you must subclass that model from
    "django_singleton_app_name.models.SingletonBaseModel"
    And create a ModelAdmin for that model that subclasses
    "django_singleton_app_name.admin.SingletonModelAdmin"
    and overwrite the ModelAdmin's member "model" with the Model's class
    Example:
    class ContactInformation(SingletonBaseModel):
        address = models.CharField(max_length=65)
        email = models.EmailField()
        
    class ContactInfoAdmin(SingletonModelAdmin):
        model = ContactInformation
    