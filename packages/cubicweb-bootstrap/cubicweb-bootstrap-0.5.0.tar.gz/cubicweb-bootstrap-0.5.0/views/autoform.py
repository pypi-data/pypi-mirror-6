"""bootstrap implementation of autoforms

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb import tags
from logilab.mtconverter import xml_escape

from cubicweb.web import formwidgets, stdmsgs
from cubicweb.web.views.autoform import AutomaticEntityForm
from cubicweb.web.views.editforms import DeleteConfForm

stdmsgs.BUTTON_OK = (stdmsgs.BUTTON_OK[0], 'glyphicon-ok')
stdmsgs.BUTTON_APPLY = (stdmsgs.BUTTON_APPLY[0], 'glyphicon-cog')
stdmsgs.BUTTON_CANCEL = (stdmsgs.BUTTON_CANCEL[0], 'glyphicon-refresh')
stdmsgs.BUTTON_DELETE = (stdmsgs.BUTTON_DELETE[0], 'glyphicon-trash')


class BootstrapButton(formwidgets.Button):
    """Override default form buttons to 'btn-class' and use bootstrap glyphicons.

    Keep the `validateButton` as it is used in js (e.g `unfreezeFormButtons`)
    """
    css_class = 'btn btn-default validateButton'

    def render(self, form, field=None, renderer=None):
        label = form._cw._(self.label)
        attrs = self.attrs.copy()
        if self.cwaction:
            assert self.onclick is None
            attrs['onclick'] = "postForm('__action_%s', \'%s\', \'%s\')" % (
                self.cwaction, self.label, form.domid)
        elif self.onclick:
            attrs['onclick'] = self.onclick
        if self.name:
            attrs['name'] = self.name
            if self.setdomid:
                attrs['id'] = self.name
        if self.settabindex and not 'tabindex' in attrs:
            attrs['tabindex'] = form._cw.next_tabindex()
        if self.icon:
            img = u'<i class="glyphicon %s"> </i>' % self.icon
        else:
            img = u''
        return tags.button(img + xml_escape(label), escapecontent=False,
                           value=label, type=self.type, **attrs)

class BootstrapSubmitButton(BootstrapButton):
    type = 'submit'
    css_class = 'btn btn-primary validateButton'


# override default form buttons:
# - use bootstrap buttons,

AutomaticEntityForm.form_buttons = [
    BootstrapSubmitButton(stdmsgs.BUTTON_OK, cwaction='apply'),
    BootstrapButton(stdmsgs.BUTTON_APPLY, cwaction='apply'),
    BootstrapButton(stdmsgs.BUTTON_CANCEL, cwaction='cancel'),
    ]

DeleteConfForm.form_buttons = [
    BootstrapButton(stdmsgs.BUTTON_DELETE, cwaction='delete',
                    attrs={'class': 'btn btn-danger validateButton'}),
    BootstrapButton(stdmsgs.BUTTON_CANCEL, cwaction='cancel'),
    ]
