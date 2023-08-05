from five import grok

from seantis.plonetools import tools
from seantis.kantonsrat.interfaces import ISeantisKantonsratSpecific


class BaseView(grok.View):

    grok.baseclass()
    grok.layer(ISeantisKantonsratSpecific)

    def translate(self, text):
        return tools.translator(self.request, 'seantis.people')(text)
