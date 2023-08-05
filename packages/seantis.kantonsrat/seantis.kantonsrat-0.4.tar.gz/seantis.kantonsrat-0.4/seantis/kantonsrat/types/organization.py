from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.indexer import indexer
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.dexterity.content import Container
from plone.directives import form

from collective.dexteritytextindexer import searchable

from seantis.kantonsrat import _


organization_types = SimpleVocabulary(
    [
        SimpleTerm(value='committee', title=_(u'Committee')),
        SimpleTerm(value='faction', title=_(u'Faction')),
        SimpleTerm(value='party', title=_(u'Party'))
    ]
)


class IOrganization(form.Schema):

    searchable('type')
    type = schema.Choice(
        title=_(u'Type'),
        source=organization_types,
        default='committee'
    )

    searchable('title')
    title = schema.TextLine(
        title=_(u'Title')
    )

    searchable('description')
    description = schema.Text(
        title=_(u'Description')
    )

    searchable('portrait')
    form.widget(portrait=WysiwygFieldWidget)
    portrait = schema.Text(
        title=_(u'Portrait'),
        required=False
    )


@indexer(IOrganization)
def organization_type(obj):
    return obj.type


class Organization(Container):
    pass
