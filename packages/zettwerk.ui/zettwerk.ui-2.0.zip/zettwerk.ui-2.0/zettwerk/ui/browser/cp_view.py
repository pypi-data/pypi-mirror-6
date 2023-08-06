## ControlPanel form for the UITool

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser import DisplayWidget
from zope.i18n import translate

from zope.component import adapts
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from ..tool.tool import IUITool, IUIToolTheme, \
    IUIToolThemeroller
from zettwerk.ui import messageFactory as _
from ..filesystem import isAvailable, DOWNLOAD_HOME


class UIControlPanelAdapter(SchemaAdapterBase):
    """ Adapter for the interface schema fields """

    adapts(IPloneSiteRoot)
    implements(IUITool)

    def __init__(self, context):
        super(UIControlPanelAdapter, self).__init__(context)
        self.portal = context
        ui_tool = getToolByName(self.portal, 'portal_ui_tool')
        self.context = ui_tool

theme = FormFieldsets(IUIToolTheme)
theme.id = 'theme'
theme.label = _(u"Existing themes")
theme.description = _(u'Please select a theme from the existing ones.')

themeroller = FormFieldsets(IUIToolThemeroller)
themeroller.id = 'themeroller'
themeroller.label = _('Add theme')


class ThemeDisplayWidget(DisplayWidget):
    """ Display the create directory link """

    def __call__(self):
        tool = self.context.context
        tool._rebuildThemeHashes()

        create_help = translate(_(u"Create download directory at: "),
                                domain="zettwerk.ui",
                                context=self.request)
        create_text = "%s <br />%s" % (create_help, DOWNLOAD_HOME)
        create_dl = u'<a class="createDLD" ' \
            u'href="javascript:createDLDirectory()">%s</a>' % (create_text)

        if isAvailable():
            return _(u"add_theme_description_text", """<p>Sadly,
            the on the fly themeroller integration does not work anymore. But
            it is possible, to download and add new themes by hand. There are
            two kind of themes: Jquery UI Default themes and custom ones.</p>
            <p>To include all the default themes follow these steps:
            <ol>
            <li>Download the zip file from <a href="http://jqueryui.com/resources/download/jquery-ui-themes-1.9.2.zip">http://jqueryui.com/resources/download/jquery-ui-themes-1.9.2.zip</a></li>
            <li>Extract the contents/subfolders of the themes folder to your zettwerk.ui download directory.</li>
            <li>Reload this page and choose a theme.</li>
            </ol>
            </p>
            <p style="margin-top: 2em">To include a custom theme follow these steps:
            <ol>
            <li>Go to the themeroller page at <a target="_blank" href="http://jqueryui.com/themeroller/">http://jqueryui.com/themeroller/</a> and create your theme with the themeroller tool.</li>
            <li>Click Download theme (in the themeroller widget)</li>
            <li>On the next page, choose the legacy Version (1.9.2 at the moment)</li>
            <li>Scroll to the bottom of the page set a folder name which gets the theme name.</li>
            <li>Click download</li>
            <li>Extract the folder css/$your_theme_name to your zettwerk.ui download directory.</li>
            <li>Reload this page and choose a theme.</li>
            </ol>
            </p>
            """)
        else:
            return create_dl


class UIControlPanel(ControlPanelForm):
    """ Build the ControlPanel form. """

    form_fields = FormFieldsets(theme, themeroller)
    form_fields['themeroller'].custom_widget = ThemeDisplayWidget
    form_fields['themeroller'].for_display = True

    label = _(u"Zettwerk UI Themer")
    description = ''

    # def __call__(self):
    #
