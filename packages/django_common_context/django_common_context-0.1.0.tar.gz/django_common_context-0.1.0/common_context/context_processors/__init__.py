# -*- coding: utf-8 -*-
##############################################################################
#
#    Django Common Context Processors
#    Copyright (C) 2014 Mariano Ruiz <mrsarm@gmail.com>
#    All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this programe.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from django import conf
from django.utils.functional import SimpleLazyObject

def site(request):
    """
    Return the current site.
    """
    from django.contrib.sites.models import get_current_site
    return {
        'site': SimpleLazyObject(lambda: get_current_site(request)),
    }

def settings(request):
    """
    Return Django settings.
    """
    return {'settings': conf.settings}
