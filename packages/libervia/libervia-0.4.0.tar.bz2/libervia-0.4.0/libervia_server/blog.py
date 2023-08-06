#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011, 2012, 2013, 2014 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat_frontends.tools.strings import addURLToText
from libervia_server.html_tools import sanitizeHtml
from twisted.internet import reactor, defer
from twisted.web import server
from twisted.web.resource import Resource
from twisted.words.protocols.jabber.jid import JID
from datetime import datetime
from feed import atom
from constants import Const


class MicroBlog(Resource):
    isLeaf = True

    ERROR_TEMPLATE = """
                <html>
                <head>
                    <title>MICROBLOG ERROR</title>
                </head>
                <body>
                    <h1 style='text-align: center; color: red;'>%s</h1>
                </body>
                </html>
                """

    def __init__(self, host):
        self.host = host
        Resource.__init__(self)
        if not host.bridge.isConnected("libervia"):  # FIXME: hard coded value for test
            host.bridge.connect("libervia")

    def render_GET(self, request):
        if not request.postpath:
            return MicroBlog.ERROR_TEMPLATE % "You must indicate a nickname"
        else:
            prof_requested = request.postpath[0]
            #TODO: char check: only use alphanumerical chars + some extra(_,-,...) here
            prof_found = self.host.bridge.getProfileName(prof_requested)
            if not prof_found or prof_found == 'libervia':
                return MicroBlog.ERROR_TEMPLATE % "Invalid nickname"
            else:
                def got_jid(pub_jid_s):
                    pub_jid = JID(pub_jid_s)
                    d2 = defer.Deferred()
                    if len(request.postpath) > 1 and request.postpath[1] == 'atom.xml':
                        d2.addCallbacks(self.render_atom_feed, self.render_error_blog, [request], None, [request, prof_found], None)
                        self.host.bridge.getLastGroupBlogsAtom(pub_jid.userhost(), 10, 'libervia', d2.callback, d2.errback)
                    else:
                        d2.addCallbacks(self.render_html_blog, self.render_error_blog, [request, prof_found], None, [request, prof_found], None)
                        self.host.bridge.getLastGroupBlogs(pub_jid.userhost(), 10, 'libervia', d2.callback, d2.errback)

                d1 = defer.Deferred()
                JID(self.host.bridge.asyncGetParamA('JabberID', 'Connection', 'value', Const.SERVER_SECURITY_LIMIT, prof_found, callback=d1.callback, errback=d1.errback))
                d1.addCallbacks(got_jid)

                return server.NOT_DONE_YET

    def render_html_blog(self, mblog_data, request, profile):
        user = sanitizeHtml(profile).encode('utf-8')
        request.write("""
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <link rel="alternate" type="application/atom+xml" href="%(user)s/atom.xml"/>
                <link rel="stylesheet" type="text/css" href="../css/blog.css" />
                <title>%(user)s's microblog</title>
            </head>
            <body>
                <div class='mblog_title'>%(user)s</div>
            """ % {'user': user})
        mblog_data = sorted(mblog_data, key=lambda entry: (-float(entry.get('published', 0))))
        for entry in mblog_data:
            timestamp = float(entry.get('published', 0))
            _datetime = datetime.fromtimestamp(timestamp)

            def getText(key):
                if ('%s_xhtml' % key) in entry:
                    return entry['%s_xhtml' % key].encode('utf-8')
                elif key in entry:
                    processor = addURLToText if key.startswith('content') else sanitizeHtml
                    return processor(entry[key]).encode('utf-8')
                return ''

            body = getText('content')
            title = getText('title')
            if title:
                body = "<h1>%s</h1>\n%s" % (title, body)
            request.write("""<div class='mblog_entry'><span class='mblog_timestamp'>%(date)s</span>
                          <span class='mblog_content'>%(content)s</span></div>""" % {
                          'date': _datetime,
                          'content': body})
        request.write('</body></html>')
        request.finish()

    def render_atom_feed(self, feed, request):
        request.write(feed.encode('utf-8'))
        request.finish()

    def render_error_blog(self, error, request, profile):
        request.write(MicroBlog.ERROR_TEMPLATE % "Can't access requested data")
        request.finish()
