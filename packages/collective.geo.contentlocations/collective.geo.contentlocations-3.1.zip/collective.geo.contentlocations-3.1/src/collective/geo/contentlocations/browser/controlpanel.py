from plone.z3cform.fieldsets import extensible
from collective.geo.settings.interfaces import IGeoSettings
from z3c.form import field


class GeoControlpanelFormExtender(extensible.FormExtender):

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        # add geo_content_types field to controlpanel form
        fields = field.Fields(IGeoSettings).select('geo_content_types')
        if 'geo_content_types' not in self.form.fields:
            self.add(fields, index=0)
