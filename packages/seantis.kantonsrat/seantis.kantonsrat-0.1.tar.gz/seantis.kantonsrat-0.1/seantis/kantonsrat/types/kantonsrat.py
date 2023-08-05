from plone.directives import form
from seantis.people.types.base import PersonBase


class IMember(form.Schema):
    form.model("kantonsrat.xml")


class Member(PersonBase):
    pass
