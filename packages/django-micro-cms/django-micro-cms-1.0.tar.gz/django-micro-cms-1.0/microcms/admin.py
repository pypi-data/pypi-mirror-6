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


from django.contrib import admin

from .models import Page, PageContent, Template

class ContentInline(admin.TabularInline):
    model = PageContent
    extra = 1

class PageAdmin(admin.ModelAdmin):
    model = Page
    inlines = (ContentInline, )


admin.site.register(Page, PageAdmin)
admin.site.register(Template)
