# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

import json
from cubicweb.devtools.httptest import CubicWebServerTC

try:
    # ensure a recent request lib is available
    import requests
    assert [int(n) for n in requests.__version__.split('.', 2)][:2] >= [1, 2]
except (ImportError, AssertionError):
    requests = None


class RqlIOTc(CubicWebServerTC):

    def setUp(self):
        "Skip whole test class if a suitable requests module is not available"
        if requests is None:
            self.skipTest('Python ``requests`` module is not available')
        super(RqlIOTc, self).setUp()


    def test_queries(self):
        req = self.request()
        args = [('INSERT CWUser U: U login %(l)s, U upassword %(p)s',
                 {'l': 'Babar', 'p': 'cubicweb rulez & 42'}),
                ('INSERT CWGroup G: G name "pachyderms"', {}),
                ('SET U in_group G WHERE U eid %(u)s, G eid %(g)s',
                 {'u': '__r0', 'g': '__r1'})]
        queries = json.dumps(args)
        a = requests.post(req.build_url('rqlio/1.0'), data=queries, headers={'Content-Type': 'application/json'})
        self.assertEqual(a.status_code, 200)
        # anonymous never get anything because we don't even
        # try to execute stuff

        # as a standard user
        self.create_user(req, u'toto', password=u'toto')
        req = self.request()

        r = requests.Session()
        a = r.get(req.base_url() + "?__login=toto&__password=toto")
        a = r.post(req.build_url('rqlio/1.0'), data=queries, headers={'Content-Type': 'application/json'})
        # remote call fails because we're not allowed to SET U in_group G
        self.assertEqual({'reason': 'You are not allowed to perform add operation '
                          'on relation CWUser in_group CWGroup'},
                         a.json())


        # now, as an admin
        r = requests.Session()
        a = r.get(req.base_url() + "?__login=admin&__password=gingkow")
        a = r.post(req.build_url('rqlio/1.0'), data=queries, headers={'Content-Type': 'application/json'})

        self.assertEqual('pachyderms',
                         self.execute('Any N WHERE U in_group G, U login "Babar", '
                                      'G name N').rows[0][0])
        output = [x for x, in a.json()]
        self.assertEqual(1, len(output[0]))
        self.assertEqual(1, len(output[1]))
        self.assertEqual(2, len(output[2]))
        self.assertEqual([output[0][0], output[1][0]], output[2])
