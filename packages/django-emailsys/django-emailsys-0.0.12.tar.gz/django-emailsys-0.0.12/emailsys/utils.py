from emailsys.settings import CONTENT_TYPE
from django.template import loader, Context

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
