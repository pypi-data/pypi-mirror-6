# encoding: utf-8
from five import grok

from ..cktemplate import ICKTemplateFolder


class CKTemplateListingView(grok.View):
    grok.context(ICKTemplateFolder)
    grok.name('cktemplate-listing.js')
    grok.require('zope2.View')

    @property
    def templates(self):
        templates = []
        for brain in self.context.portal_catalog(portal_type='cktemplate',
                                                 review_state=('enabled', )):
            template = brain.getObject()
            if template.can_view(self.context) is True:
                templates.append((template, brain.getPath()))
        return templates

    def render(self):
        self.request.response.setHeader('Content-Type',
                                        'application/javascript')
        return """CKEDITOR.addTemplates('default',
{
    imagesPath: CKEDITOR.getUrl('../../'),
    templates: [
        %s
    ]
});""" % ", ".join([self.render_template(t, p) for t, p in self.templates])

    def render_template(self, template, path):
        base = ('{title: "%(title)s", %(image)s'
                'description: "%(description)s", '
                'html: "%(html)s"}')
        icon = ''
        if template.custom_icon is not None:
            icon = 'image: "%s/%s", ' % (path, template.image)
        return base % {
            u'title': template.title.replace('"', '&quot;'),
            u'image': icon,
            u'description': template.description.replace('"', '&quot;'),
            u'html': template.html}
