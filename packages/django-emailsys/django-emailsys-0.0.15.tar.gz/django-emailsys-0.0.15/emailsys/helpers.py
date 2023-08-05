from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.template import loader, Context
from emailsys.settings import CONTENT_TYPE

def get_module_class(class_path):
    """
    imports and returns module class from ``path.to.module.Class`` argument
    """
    mod_name, cls_name = class_path.rsplit('.', 1)

    try:
        mod = import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' % (mod_name, e)))

    return getattr(mod, cls_name)

def get_message_template(template, context=None):
    """
    Send email rendering text and html versions for the specified
    template name using the context dictionary passed in.
    """
    if context is None:
        context = {}

    # Loads a template passing in vars as context.
    def render(ext):
        name = "emailsys/%s.%s" % (template, ext)
        return loader.get_template(name).render(Context(context))

    return render(CONTENT_TYPE.lower())