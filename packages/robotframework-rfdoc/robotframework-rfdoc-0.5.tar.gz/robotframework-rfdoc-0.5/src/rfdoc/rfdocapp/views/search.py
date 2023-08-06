# Copyright 2009-2013 Nokia Siemens Networks Oyj
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from django import forms
from django.db.models import Q
from django.shortcuts import render_to_response

from rfdocapp.models import Keyword


def search(request):
    search_performed = False
    kws = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            term = form.cleaned_data['search_term']
            version = form.cleaned_data['search_version']
            query = Q(name__icontains = term)
            if form.cleaned_data['include_doc']:
                query = query | Q(doc__icontains = term)
            # SQLite LIKEs are case-insensitive by default.
            # Thus using just name__contains wouldn't work expectedly.
            # To circumvent this, an additional query using regular expressions
            # is applied for the case-sensitive searches.
            if not form.cleaned_data['case_insensitive']:
                query = Q(name__regex = r'.*%s.*' % re.escape(term))
                if form.cleaned_data['include_doc']:
                    query = query | Q(doc__regex = r'.*%s.*' % re.escape(term))
            kws = Keyword.objects.filter(query)
            if version:
                version = re.escape(version).replace('\?','.').replace('\*','.*')
                kws = kws.filter(library__version__regex=r'^%s$' % version)
            search_performed = True
    else:
        form = SearchForm()
    return render_to_response('search.html', {
            'form': form,
            'kws': kws,
            'search_performed': search_performed
        }
    )


class SearchForm(forms.Form):
    search_term = forms.CharField(error_messages={'required': 'Search term is required!'})
    search_version = forms.CharField(required=False)
    include_doc = forms.BooleanField(required=False, initial=True)
    case_insensitive = forms.BooleanField(required=False, initial=True)

