from plone.app.discussion.browser.comments import CommentsViewlet
class ConversationView(object):
    """ Ability to either allow / disallow comments based on schema
option
    """
    def enabled(self):
        return getattr(self.context, 'allowDiscussion', False) 
