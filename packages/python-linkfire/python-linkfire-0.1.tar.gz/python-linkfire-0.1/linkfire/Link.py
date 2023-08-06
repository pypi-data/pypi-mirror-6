from .Base import ApiMethod

class Link(ApiMethod):
    """Link class to make a new shortlink"""
    
    original_url = ""
    shortlink = None

    title = ""
    description = ""
    thumbnail = None

    def __init__(self, url, title, description):
        super(Link, self).__init__()
        self.original_url = url
        self.title = title
        self.description = description

    def make_it_shorter(self):
        """
            This function will make the url a short link.
        """
        payload = {
            "url": self.original_url,
            "title": self.title,
            "description": self.description,
        }
        data = self.call_api("links/create", payload, method="post")

        self.shortlink = data['link']['url']
        self.original_url = data['link']['original_url']

    def __unicode__(self):
        return u"%s" % self.shortlink

    def __str__(self):
        return "%s" % self.shortlink