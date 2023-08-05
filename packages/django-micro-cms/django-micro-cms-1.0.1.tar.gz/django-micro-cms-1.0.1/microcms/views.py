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
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Count
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from .models import Page, PageContent, Template


########################################################################
# open questions
# * how would you make a page where no fallback exists (but a page in the
#   original language does)?
#   At the moment, we simply ignore this fact because none of the
#   current uses require this feature. If it becomes necessary, it
#   would probably be best to add a flag to the page indicating
#   whether a fallback is required.
# * Does the content get escaped or transformed?
#   No, currently not. It would be easy to add markdown or
#   reStructuredText formatting.
# * Is there an editor?
#   No, there is currently not. You can use tinymce in your admin to
#   make life easier for you when editing pages, but nothing is
#   integrated at the moment.
#
########################################################################

def pages(request, url):

    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect(request.path + '/')

    # get the page object, but only if it has content associated with it
    try:
        page = Page.objects.annotate(
            content_count=Count('pagecontent')
        ).get(url__exact=url, content_count__gte=1)
        page_lang = settings.LANGUAGE_CODE
        activate_lang = False
    except Page.DoesNotExist:
        urlparts = url.split('/')
        if len(urlparts) > 2:
            # skip the first TWO parts of the URL because the first
            # will be empty (before the first slash) and the second
            # will be the actual language code
            page_lang = urlparts[1]
            activate_lang = True
            urlrest = '/' + '/'.join(urlparts[2:])
            try:
                page = Page.objects.annotate(content_count=Count('pagecontent')).get(url__exact=urlrest, content_count__gte=1)
            except Page.DoesNotExist:
                raise Http404(_('Page not found'))
        else:
            raise Http404(_('Page not found'))
        
    # get correct language version
    # going from specific to unspecific: full code, short code,
    # fallback, fallback-short 
    full_lang      = page_lang
    short_lang     = full_lang[:2]
    fallback_lang  = settings.LANGUAGE_CODE
    fallshort_lang = fallback_lang[:2]

    # FUN!
    try:
        content = PageContent.objects.get(
            page=page,
            language_code=full_lang)
    except PageContent.DoesNotExist:
        try:
            content = PageContent.objects.get(
                page=page,
                language_code=short_lang)
        except PageContent.DoesNotExist:
            try:
                content = PageContent.objects.get(
                    page=page,
                    language_code=fallback_lang)
            except PageContent.DoesNotExist:
                try:
                    content = PageContent.objects.get(
                        page=page,
                        language_code=fallshort_lang)
                except PageContent.DoesNotExist:
                    raise Http404(_('No content found.'))

    if activate_lang:
        # if the user requested a specific language version, we will
        # activate that version, even if another language version was
        # loaded
        from django.utils import translation
        translation.activate(page_lang)
        
    return render_page(request, page, content)
                


@csrf_protect
def render_page(request, page, content):

    t = page.template
    c = RequestContext(
        request,
        {
        'title':   mark_safe(page.title),
        'content': mark_safe(content.content),
        'CONTENT_LANGUAGE_CODE': content.language_code,
        'created': content.created,
        'last_modified': content.modified,
        }
    )

    return HttpResponse(t.render(c))
