from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.slideshare import slideshareMessageFactory as _

def _create_policy_vocab():
    items = [ ("fixed", _(u"always use credentials below")),
        ("user", _("always ask user for his credentials")),
        ("optional", _("allow user to supply his credentials"))]

    return  [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in items ]


user_policy_vocabulary = SimpleVocabulary(_create_policy_vocab())

