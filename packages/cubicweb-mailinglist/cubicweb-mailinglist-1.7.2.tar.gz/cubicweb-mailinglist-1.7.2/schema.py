from yams.buildobjs import EntityType, String, RichString
from yams.reader import context

class MailingList(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners'),
    }
    ## attributes
    name  = String(fulltextindexed=True, maxsize=64)
    mlid  = String(indexed=True, maxsize=64,
                   description=_('mailing list id specified in messages header'))
    description = RichString(fulltextindexed=True, maxsize=512)

    email_address = String(required=1, maxsize=256,
                           description=_("email address to use to post on the mailing-list"))
    archive = String(maxsize=256, description=_("URL of the mailing-list's archive"))
    homepage = String(maxsize=256, description=_("URL of the mailing-list's admin page"))


if 'Email' in context.defined:
    class sent_on(RelationDefinition):
        """mailing list on which the email was sent"""
        subject = 'Email'
        object = 'MailingList'
