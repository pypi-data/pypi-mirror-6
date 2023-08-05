import re
import requests
from StringIO import StringIO

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from w3c_validator.validator import Validator


from debug_toolbar.panels import Panel


class W3CValidatorPanel(Panel):
    nav_title = _("W3C Validator")
    has_content = True

    title = _("W3C Validator")
    template = 'w3c_validator/panel.html'

    log_data = None
    errors_count = 0
    warns_count = 0
    src_content = ''

    @property
    def nav_subtitle(self):
        stats = self.get_stats()
        return mark_safe(
            _(u"Errors: {errors_count} "
              u"Warnings: {warns_count}").format(**stats)

            )

    def process_response(self, request, response):
        self.validator = Validator()
        self.validator.validate_source(response.content)
        self.src = response.content.split("\n")
        stats = dict(
            errors=self.validator.errors,
            warnings=self.validator.warnings,
            errors_count=self.validator.error_count,
            warns_count=self.validator.warning_count,
        )
        self.record_stats(stats)
        return response