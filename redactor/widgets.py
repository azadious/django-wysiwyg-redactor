import json
from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings


GLOBAL_OPTIONS = getattr(settings, 'REDACTOR_OPTIONS', {})


class RedactorEditor(widgets.Textarea):
    init_js = '''<script type="text/javascript">
                    jQuery(document).ready(function(jQuery){
                        var $field = jQuery("#%s");
                        options = %s;
                        options.imageUploadErrorCallback = function(json){
                            alert(json.error);
                        };
                        $field.redactor(options);
                    });
                 </script>
              '''

    def __init__(self, *args, **kwargs):
        upload_to = kwargs.pop('upload_to', '')
        custom_options = kwargs.pop('redactor_options', {})
        allow_file_upload = kwargs.pop('allow_file_upload', True)
        allow_image_upload = kwargs.pop('allow_image_upload', True)

        options = GLOBAL_OPTIONS.copy()
        options.update(custom_options)
        if allow_file_upload:
            options['fileUpload'] = reverse(
                'redactor_upload_file',
                kwargs={'upload_to': upload_to}
            )
        if allow_image_upload:
            options['imageUpload'] = reverse(
                'redactor_upload_image',
                kwargs={'upload_to': upload_to}
            )
        self.options = options
        super(RedactorEditor, self).__init__(*args, **kwargs)

    def json_options(self):
        return json.dumps(self.options)

    def render(self, name, value, attrs=None):
        html = super(RedactorEditor, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id')
        html += self.init_js % (id_, self.json_options())
        return mark_safe(html)

    def _media(self):
        js = (
            'redactor/jquery.redactor.init.js',
            'redactor/redactor.js',
            'redactor/langs/{0}.js'.format(GLOBAL_OPTIONS.get('lang', 'en')),
        )

        if self.options.has_key('plugins'):
            plugins = self.options.get('plugins')
            for plugin in plugins:
                js = js + (
                    'redactor/plugins/{0}.js'.format(plugin),
                )

        js = js + (
            'redactor/langs/{0}.js'.format(GLOBAL_OPTIONS.get('lang', 'en')),
        )

        css = {
            'all': (
                'redactor/css/redactor.css',
                'redactor/css/django_admin.css',
            )
        }
        return forms.Media(css=css, js=js)
    media = property(_media)
