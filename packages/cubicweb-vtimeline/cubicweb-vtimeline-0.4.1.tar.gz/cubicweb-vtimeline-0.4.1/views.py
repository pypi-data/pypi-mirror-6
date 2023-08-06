# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-vtimeline views/forms/actions/components for web ui"""

import json

from logilab.common.date import ustrftime
from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.predicates import one_line_rset, is_instance, adaptable
from cubicweb.utils import json_dumps, make_uid


class VeriteCoTimelineJsonDataView(EntityView):
    __regid__ = 'vtimeline.json'
    __select__ = adaptable('ICalendarable')
    template = False
    content_type = 'application/json'
    binary = True

    def call(self):
        dates = []
        d = {'timeline': {
                'headline': '',
                'type': 'default',
                'text': '',
                'date': dates
                }
             }
        for entity in self.cw_rset.entities():
            calendarable = entity.cw_adapt_to('ICalendarable')
            depictable = entity.cw_adapt_to('IDepictable')
            if depictable is None:
                depiction_url =  thumbnail_url = None
            else:
                depiction_url = depictable.depiction_url()
                thumbnail_url = depictable.thumbnail_url()
            if calendarable.start:
                dates.append({'startDate': ustrftime(calendarable.start, '%Y,%m,%d'),
                              'headline': entity.view('incontext'),
                              'text': entity.view('vtimeline-itemdescr'),
                              #'mediameta': {'type': 'image', 'id': depiction_url},
                              'asset': {'media': depiction_url,
                                        'credit': u'', 'caption': u'',
                                        'thumbnail': thumbnail_url,
                                        'mediameta': {'type': 'image', 'id': depiction_url},
                                        },
                              'thumbnail': thumbnail_url,
                              })
        self.w(json.dumps(d))

def mergedicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result

class VTimelineItemView(EntityView):
    __regid__ = 'vtimeline-itemdescr'
    __select__ = adaptable('ICalendarable')

    def entity_call(self, entity):
        self.w(u'<p>%s</p>' % entity.dc_description())

class VeriteCoTimelineView(EntityView):
    __regid__ = 'vtimeline'
    __select__ = adaptable('ICalendarable')

    default_settings = {
        'width': '600', # could be an expression such as '$("#pageContent").width()'
        'height': '400',
        'start_at_slide': 0,
        }

    def call(self, custom_settings={}):
        settings = self.build_settings(custom_settings)
        self.w(u'<div id="%(embed_id)s"></div>' % settings)
        self._cw.html_headers.define_var('embed_path', self._cw.data_url('veritejs/'))
        self._cw.add_js('veritejs/js/storyjs-embed.js')
        self._cw.add_onload(self.js_story_factory(settings))

    def js_story_factory(self, settings):
        return 'createStoryJS(%s)' % json_dumps(settings)

    def build_settings(self, custom_settings):
        divid = make_uid('t')
        json_url = self._cw.build_url('view', rql=self.cw_rset.printable_rql(),
                                      vid='vtimeline.json')
        return mergedicts({'lang': self._cw.lang,
                           'type': 'timeline',
                           'embed_id': divid,
                           'debug': False,
                           'source': json_url,},
                            self.default_settings,
                            custom_settings)
