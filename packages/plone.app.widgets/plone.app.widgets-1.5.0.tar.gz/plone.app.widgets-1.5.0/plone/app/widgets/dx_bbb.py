# -*- coding: utf-8 -*-
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.behaviors.metadata import IOwnership
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.app.widgets.dx import AjaxSelectWidget
from plone.app.widgets.dx import DatetimeWidget
from plone.app.widgets.dx import QueryStringWidget
from plone.app.widgets.dx import RelatedItemsFieldWidget
from plone.app.widgets.dx import RichTextWidget
from plone.app.widgets.dx import SelectWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.app.widgets.utils import first_weekday
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer

try:
    from plone.app.relationfield.behavior import IRelatedItems
    HAS_RF = True
except ImportError:
    HAS_RF = False

try:
    from plone.app.contenttypes.behaviors.collection import ICollection
    from plone.app.contenttypes.behaviors.richtext import IRichText
    HAS_PAC = True
except ImportError:
    HAS_PAC = False

try:
    from plone.app.event.dx.behaviors import IEventBasic
    HAS_PAE = True
except ImportError:
    HAS_PAE = False


@adapter(getSpecification(ICategorization['subjects']), IWidgetsLayer)
@implementer(IFieldWidget)
def SubjectsFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Keywords'
    return widget


@adapter(getSpecification(ICategorization['language']), IWidgetsLayer)
@implementer(IFieldWidget)
def LanguageFieldWidget(field, request):
    widget = FieldWidget(field, SelectWidget(request))
    return widget


@adapter(getSpecification(IPublication['effective']), IWidgetsLayer)
@implementer(IFieldWidget)
def EffectiveDateFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    widget.pattern_options.setdefault('date', {})
    widget.pattern_options['date']['firstDay'] = first_weekday()
    return widget


@adapter(getSpecification(IPublication['expires']), IWidgetsLayer)
@implementer(IFieldWidget)
def ExpirationDateFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    widget.pattern_options.setdefault('date', {})
    widget.pattern_options['date']['firstDay'] = first_weekday()
    return widget


@adapter(getSpecification(IOwnership['contributors']), IWidgetsLayer)
@implementer(IFieldWidget)
def ContributorsFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Users'
    return widget


@adapter(getSpecification(IOwnership['creators']), IWidgetsLayer)
@implementer(IFieldWidget)
def CreatorsFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Users'
    return widget


if HAS_RF:
    RelatedItemsFieldWidget = adapter(
        getSpecification(IRelatedItems['relatedItems']),
        IWidgetsLayer
    )(RelatedItemsFieldWidget)

if HAS_PAC:
    @adapter(getSpecification(ICollection['query']), IWidgetsLayer)
    @implementer(IFieldWidget)
    def QueryStringFieldWidget(field, request):
        return FieldWidget(field, QueryStringWidget(request))

    @adapter(getSpecification(IRichText['text']), IWidgetsLayer)
    @implementer(IFieldWidget)
    def RichTextFieldWidget(field, request):
        return FieldWidget(field, RichTextWidget(request))

if HAS_PAE:
    @adapter(getSpecification(IEventBasic['start']), IWidgetsLayer)
    @implementer(IFieldWidget)
    def StartDateFieldWidget(field, request):
        return FieldWidget(field, DatetimeWidget(request))

    @adapter(getSpecification(IEventBasic['end']), IWidgetsLayer)
    @implementer(IFieldWidget)
    def EndDateFieldWidget(field, request):
        return FieldWidget(field, DatetimeWidget(request))
