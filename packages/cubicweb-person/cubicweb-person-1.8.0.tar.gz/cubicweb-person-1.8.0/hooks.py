from cubicweb.selectors import is_instance
from cubicweb.sobjects.notification import ContentAddedView

class PersonAddedView(ContentAddedView):
    """get notified from new persons"""
    __select__ = is_instance('Person')
    content_attr = 'description'
