from zope.i18nmessageid import MessageFactory
# Set up the i18n message factory for our package
MessageFactory = MessageFactory('collective.publications')

from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.interfaces import IFormLayer
from plone.app.dexterity.behaviors.metadata import ICategorization

from five import grok

from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget

def SubjectsFieldWidget(field, request):
    field.index_name = 'Subject'
    return TokenInputFieldWidget(field, request)

grok.global_adapter(
    SubjectsFieldWidget,
    (getSpecification(ICategorization['subjects']),
     IFormLayer),
    IFieldWidget,
)

