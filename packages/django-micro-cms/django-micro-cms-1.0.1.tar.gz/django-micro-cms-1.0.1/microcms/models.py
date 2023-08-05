#
#  Copyright 2014 Johannes Spielmann <jps@shezi.de>
#
#  This file is part of django-micro-cms.
#
#  django-micro-cms is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  django-micro-cms is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with django-micro-cms.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.db import models
from django.template import Template as DjangoTemplate
from django.utils.translation import ugettext as _



class Page(models.Model):

    title = models.CharField(
        max_length=255,
        help_text=_("Page title, will be available as variable named `title` in the template.")
    )

    url = models.CharField(
        max_length=128,
        help_text=_("Make sure to have '/' at the end and the beginning, like in '/about/contact/'."),
    )
    template = models.ForeignKey('Template')
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return _("{title} @ {url}").format(title=self.title, url=self.url)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
    

class PageContent(models.Model):

    page = models.ForeignKey(Page)
    language_code = models.CharField(
        max_length=10,  # 10? yes, 10: zh-Hang-CN for example
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE[:2])
    # why is it LANGUAGE_CODE[:2]? Because USA is the center of the
    # world, and thus does the entry for american english is ('en',
    # 'English') in the LANGUAGES field, but it is 'en-us' in the
    # LANGUAGE_CODE. Sorry if you're from one of the spanish-speaking
    # countries and your default gets set back to 'es' (or you're from
    # one of the other language-variant countries like Brazil or
    # China).
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return _("content for {url} in {lang}").format(
            url=self.page.url,
            lang=self.language_code)
    
    class Meta:
        unique_together = (
            ('page', 'language_code', ),
            )
        verbose_name = _('page content part')
        verbose_name_plural = _('page content parts')
        

    

class Template(models.Model):

    title = models.CharField(
        max_length=64,
        help_text=_('This is only used to identify the template in the interface.'),
    )
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def render(self, context):
        t = DjangoTemplate(self.content)
        return t.render(context)

    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
