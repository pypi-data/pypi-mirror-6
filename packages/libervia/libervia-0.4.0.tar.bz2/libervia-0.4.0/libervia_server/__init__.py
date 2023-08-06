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

from twisted.application import internet, service
from twisted.internet import glib2reactor
glib2reactor.install()
from twisted.internet import reactor, defer
from twisted.web import server
from twisted.web import error as weberror
from twisted.web.static import File
from twisted.web.resource import Resource, NoResource
from twisted.web.util import Redirect
from twisted.python.components import registerAdapter
from twisted.python.failure import Failure
from twisted.words.protocols.jabber.jid import JID
from txjsonrpc.web import jsonrpc
from txjsonrpc import jsonrpclib

from logging import debug, info, warning, error
import re, glob
import os.path, sys
import tempfile, shutil, uuid
from zope.interface import Interface, Attribute, implements
from xml.dom import minidom

from constants import Const
from libervia_server.blog import MicroBlog
from sat_frontends.bridge.DBus import DBusBridgeFrontend, BridgeExceptionNoService
from sat.core.i18n import _, D_
from sat.tools.xml_tools import paramsXML2XMLUI


class ISATSession(Interface):
    profile = Attribute("Sat profile")
    jid = Attribute("JID associated with the profile")

class SATSession(object):
    implements(ISATSession)
    def __init__(self, session):
        self.profile = None
        self.jid = None

class LiberviaSession(server.Session):
    sessionTimeout = Const.TIMEOUT

    def __init__(self, *args, **kwargs):
        self.__lock = False
        server.Session.__init__(self, *args, **kwargs)

    def lock(self):
        """Prevent session from expiring"""
        self.__lock = True
        self._expireCall.reset(sys.maxint)

    def unlock(self):
        """Allow session to expire again, and touch it"""
        self.__lock = False
        self.touch()

    def touch(self):
        if not self.__lock:
            server.Session.touch(self)

class ProtectedFile(File):
    """A File class which doens't show directory listing"""

    def directoryListing(self):
        return NoResource()

class SATActionIDHandler(object):
    """Manage SàT action action_id lifecycle"""
    ID_LIFETIME = 30 #after this time (in seconds), action_id will be suppressed and action result will be ignored

    def __init__(self):
        self.waiting_ids = {}

    def waitForId(self, callback, action_id, profile, *args, **kwargs):
        """Wait for an action result
        @param callback: method to call when action gave a result back
        @param action_id: action_id to wait for
        @param profile: %(doc_profile)s
        @param *args: additional argument to pass to callback
        @param **kwargs: idem"""
        action_tuple = (action_id, profile)
        self.waiting_ids[action_tuple] = (callback, args, kwargs)
        reactor.callLater(self.ID_LIFETIME, self.purgeID, action_tuple)

    def purgeID(self, action_tuple):
        """Called when an action_id has not be handled in time"""
        if action_tuple in self.waiting_ids:
            warning ("action of action_id %s [%s] has not been managed, action_id is now ignored" % action_tuple)
            del self.waiting_ids[action_tuple]

    def actionResultCb(self, answer_type, action_id, data, profile):
        """Manage the actionResult signal"""
        action_tuple = (action_id, profile)
        if action_tuple in self.waiting_ids:
            callback, args, kwargs = self.waiting_ids[action_tuple]
            del self.waiting_ids[action_tuple]
            callback(answer_type, action_id, data, *args, **kwargs)

class JSONRPCMethodManager(jsonrpc.JSONRPC):

    def __init__(self, sat_host):
        jsonrpc.JSONRPC.__init__(self)
        self.sat_host=sat_host

    def asyncBridgeCall(self, method_name, *args, **kwargs):
        """Call an asynchrone bridge method and return a deferred
        @param method_name: name of the method as a unicode
        @return: a deferred which trigger the result

        """
        d = defer.Deferred()

        def _callback(*args):
            if not args:
                d.callback(None)
            else:
                if len(args) != 1:
                    Exception("Multiple return arguments not supported")
                d.callback(args[0])

        def _errback(result):
            d.errback(Failure(jsonrpclib.Fault(Const.ERRNUM_BRIDGE_ERRBACK, unicode(result))))

        kwargs["callback"] = _callback
        kwargs["errback"] = _errback
        getattr(self.sat_host.bridge, method_name)(*args, **kwargs)
        return d


class MethodHandler(JSONRPCMethodManager):

    def __init__(self, sat_host):
        JSONRPCMethodManager.__init__(self, sat_host)
        self.authorized_params = None

    def render(self, request):
        self.session = request.getSession()
        profile = ISATSession(self.session).profile
        if not profile:
            #user is not identified, we return a jsonrpc fault
            parsed = jsonrpclib.loads(request.content.read())
            fault = jsonrpclib.Fault(Const.ERRNUM_LIBERVIA, "Not allowed") #FIXME: define some standard error codes for libervia
            return jsonrpc.JSONRPC._cbRender(self, fault, request, parsed.get('id'), parsed.get('jsonrpc'))
        return jsonrpc.JSONRPC.render(self, request)

    def jsonrpc_getProfileJid(self):
        """Return the jid of the profile"""
        sat_session = ISATSession(self.session)
        profile = sat_session.profile
        sat_session.jid = JID(self.sat_host.bridge.getParamA("JabberID", "Connection", profile_key=profile))
        return sat_session.jid.full()

    def jsonrpc_disconnect(self):
        """Disconnect the profile"""
        sat_session = ISATSession(self.session)
        profile = sat_session.profile
        self.sat_host.bridge.disconnect(profile)

    def jsonrpc_getContacts(self):
        """Return all passed args."""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getContacts(profile)

    def jsonrpc_addContact(self, entity, name, groups):
        """Subscribe to contact presence, and add it to the given groups"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.addContact(entity, profile)
        self.sat_host.bridge.updateContact(entity, name, groups, profile)

    def jsonrpc_delContact(self, entity):
        """Remove contact from contacts list"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.delContact(entity, profile)

    def jsonrpc_updateContact(self, entity, name, groups):
        """Update contact's roster item"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.updateContact(entity, name, groups, profile)

    def jsonrpc_subscription(self, sub_type, entity, name, groups):
        """Confirm (or infirm) subscription,
        and setup user roster in case of subscription"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.subscription(sub_type, entity, profile)
        if sub_type == 'subscribed':
            self.sat_host.bridge.updateContact(entity, name, groups, profile)

    def jsonrpc_getWaitingSub(self):
        """Return list of room already joined by user"""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getWaitingSub(profile)

    def jsonrpc_setStatus(self, presence, status):
        """Change the presence and/or status
        @param presence: value from ("", "chat", "away", "dnd", "xa")
        @param status: any string to describe your status
        """
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.setPresence('', presence, 0, {'': status}, profile)


    def jsonrpc_sendMessage(self, to_jid, msg, subject, type_, options={}):
        """send message"""
        profile = ISATSession(self.session).profile
        return self.asyncBridgeCall("sendMessage", to_jid, msg, subject, type_, options, profile)

    def jsonrpc_sendMblog(self, type_, dest, text, extra={}):
        """ Send microblog message
        @param type_: one of "PUBLIC", "GROUP"
        @param dest: destinees (list of groups, ignored for "PUBLIC")
        @param text: microblog's text
        """
        profile = ISATSession(self.session).profile
        extra['allow_comments'] = 'True'

        if not type_:  # auto-detect
            type_ = "PUBLIC" if dest == [] else "GROUP"

        if type_ in ("PUBLIC", "GROUP") and text:
            if type_ == "PUBLIC":
                #This text if for the public microblog
                print "sending public blog"
                return self.sat_host.bridge.sendGroupBlog("PUBLIC", [], text, extra, profile)
            else:
                print "sending group blog"
                dest = dest if isinstance(dest, list) else [dest]
                return self.sat_host.bridge.sendGroupBlog("GROUP", dest, text, extra, profile)
        else:
            raise Exception("Invalid data")

    def jsonrpc_deleteMblog(self, pub_data, comments):
        """Delete a microblog node
        @param pub_data: a tuple (service, comment node identifier, item identifier)
        @param comments: comments node identifier (for main item) or False
        """
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.deleteGroupBlog(pub_data, comments if comments else '', profile)

    def jsonrpc_updateMblog(self, pub_data, comments, message, extra={}):
        """Modify a microblog node
        @param pub_data: a tuple (service, comment node identifier, item identifier)
        @param comments: comments node identifier (for main item) or False
        @param message: new message
        @param extra: dict which option name as key, which can be:
            - allow_comments: True to accept an other level of comments, False else (default: False)
            - rich: if present, contain rich text in currently selected syntax
        """
        profile = ISATSession(self.session).profile
        if comments:
            extra['allow_comments'] = 'True'
        return self.sat_host.bridge.updateGroupBlog(pub_data, comments if comments else '', message, extra, profile)

    def jsonrpc_sendMblogComment(self, node, text, extra={}):
        """ Send microblog message
        @param node: url of the comments node
        @param text: comment
        """
        profile = ISATSession(self.session).profile
        if node and text:
            return self.sat_host.bridge.sendGroupBlogComment(node, text, extra, profile)
        else:
            raise Exception("Invalid data")

    def jsonrpc_getLastMblogs(self, publisher_jid, max_item):
        """Get last microblogs posted by a contact
        @param publisher_jid: jid of the publisher
        @param max_item: number of items to ask
        @return list of microblog data (dict)"""
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("getLastGroupBlogs", publisher_jid, max_item, profile)
        return d

    def jsonrpc_getMassiveLastMblogs(self, publishers_type, publishers_list, max_item):
        """Get lasts microblogs posted by several contacts at once
        @param publishers_type: one of "ALL", "GROUP", "JID"
        @param publishers_list: list of publishers type (empty list of all, list of groups or list of jids)
        @param max_item: number of items to ask
        @return: dictionary key=publisher's jid, value=list of microblog data (dict)"""
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("getMassiveLastGroupBlogs", publishers_type, publishers_list, max_item, profile)
        self.sat_host.bridge.massiveSubscribeGroupBlogs(publishers_type, publishers_list, profile)
        return d

    def jsonrpc_getMblogComments(self, service, node):
        """Get all comments of given node
        @param service: jid of the service hosting the node
        @param node: comments node
        """
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("getGroupBlogComments", service, node, profile)
        return d


    def jsonrpc_getPresenceStatus(self):
        """Get Presence information for connected contacts"""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getPresenceStatus(profile)

    def jsonrpc_getHistory(self, from_jid, to_jid, size, between):
        """Return history for the from_jid/to_jid couple"""
        sat_session = ISATSession(self.session)
        profile = sat_session.profile
        sat_jid = sat_session.jid
        if not sat_jid:
            error("No jid saved for this profile")
            return {}
        if JID(from_jid).userhost() != sat_jid.userhost() and JID(to_jid).userhost() != sat_jid.userhost():
            error("Trying to get history from a different jid, maybe a hack attempt ?")
            return {}
        d = self.asyncBridgeCall("getHistory", from_jid, to_jid, size, between, profile)
        def show(result_dbus):
            result = []
            for line in result_dbus:
                #XXX: we have to do this stupid thing because Python D-Bus use its own types instead of standard types
                #     and txJsonRPC doesn't accept D-Bus types, resulting in a empty query
                timestamp, from_jid, to_jid, message, mess_type, extra = line
                result.append((float(timestamp), unicode(from_jid), unicode(to_jid), unicode(message), unicode(mess_type), dict(extra)))
            return result
        d.addCallback(show)
        return d

    def jsonrpc_joinMUC(self, room_jid, nick):
        """Join a Multi-User Chat room
        @room_jid: leave empty string to generate a unique name
        """
        profile = ISATSession(self.session).profile
        try:
            if room_jid != "":
                room_jid = JID(room_jid).userhost()
        except:
            warning('Invalid room jid')
            return
        d = self.asyncBridgeCall("joinMUC", room_jid, nick, {}, profile)
        return d

    def jsonrpc_inviteMUC(self, contact_jid, room_jid):
        """Invite a user to a Multi-User Chat room"""
        profile = ISATSession(self.session).profile
        try:
            room_jid = JID(room_jid).userhost()
        except:
            warning('Invalid room jid')
            return
        room_id = room_jid.split("@")[0]
        service = room_jid.split("@")[1]
        self.sat_host.bridge.inviteMUC(contact_jid, service, room_id, {}, profile)

    def jsonrpc_mucLeave(self, room_jid):
        """Quit a Multi-User Chat room"""
        profile = ISATSession(self.session).profile
        try:
            room_jid = JID(room_jid)
        except:
            warning('Invalid room jid')
            return
        self.sat_host.bridge.mucLeave(room_jid.userhost(), profile)

    def jsonrpc_getRoomsJoined(self):
        """Return list of room already joined by user"""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getRoomsJoined(profile)

    def jsonrpc_launchTarotGame(self, other_players, room_jid=""):
        """Create a room, invite the other players and start a Tarot game
        @param room_jid: leave empty string to generate a unique room name
        """
        profile = ISATSession(self.session).profile
        try:
            if room_jid != "":
                room_jid = JID(room_jid).userhost()
        except:
            warning('Invalid room jid')
            return
        self.sat_host.bridge.tarotGameLaunch(other_players, room_jid, profile)

    def jsonrpc_getTarotCardsPaths(self):
        """Give the path of all the tarot cards"""
        _join = os.path.join
        _media_dir = _join(self.sat_host.media_dir,'')
        return map(lambda x: _join(Const.MEDIA_DIR, x[len(_media_dir):]), glob.glob(_join(_media_dir, Const.CARDS_DIR, '*_*.png')));

    def jsonrpc_tarotGameReady(self, player, referee):
        """Tell to the server that we are ready to start the game"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.tarotGameReady(player, referee, profile)

    def jsonrpc_tarotGamePlayCards(self, player_nick, referee, cards):
        """Tell to the server the cards we want to put on the table"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.tarotGamePlayCards(player_nick, referee, cards, profile)

    def jsonrpc_launchRadioCollective(self, invited, room_jid=""):
        """Create a room, invite people, and start a radio collective
        @param room_jid: leave empty string to generate a unique room name
        """
        profile = ISATSession(self.session).profile
        try:
            if room_jid != "":
                room_jid = JID(room_jid).userhost()
        except:
            warning('Invalid room jid')
            return
        self.sat_host.bridge.radiocolLaunch(invited, room_jid, profile)

    def jsonrpc_getEntityData(self, jid, keys):
        """Get cached data for an entit
        @param jid: jid of contact from who we want data
        @param keys: name of data we want (list)
        @return: requested data"""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getEntityData(jid, keys, profile)

    def jsonrpc_getCard(self, jid):
        """Get VCard for entiry
        @param jid: jid of contact from who we want data
        @return: id to retrieve the profile"""
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.getCard(jid, profile)

    def jsonrpc_getParamsUI(self):
        """Return the parameters XML for profile"""
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("getParams", Const.SECURITY_LIMIT, Const.APP_NAME, profile)

        def setAuthorizedParams(params_xml):
            if self.authorized_params is None:
                self.authorized_params = {}
                for cat in minidom.parseString(params_xml.encode('utf-8')).getElementsByTagName("category"):
                    params = cat.getElementsByTagName("param")
                    params_list = [param.getAttribute("name") for param in params]
                    self.authorized_params[cat.getAttribute("name")] = params_list
            if self.authorized_params:
                return params_xml
            else:
                return None

        d.addCallback(setAuthorizedParams)

        d.addCallback(lambda params_xml: paramsXML2XMLUI(params_xml) if params_xml else "")

        return d

    def jsonrpc_asyncGetParamA(self, param, category, attribute="value"):
        """Return the parameter value for profile"""
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("asyncGetParamA", param, category, attribute, Const.SECURITY_LIMIT, profile_key=profile)
        return d

    def jsonrpc_setParam(self, name, value, category):
        profile = ISATSession(self.session).profile
        if category in self.authorized_params and name in self.authorized_params[category]:
            return self.sat_host.bridge.setParam(name, value, category, Const.SECURITY_LIMIT, profile)
        else:
            warning("Trying to set parameter '%s' in category '%s' without authorization!!!"
                    % (name, category))

    def jsonrpc_launchAction(self, callback_id, data):
        #FIXME: any action can be launched, this can be a huge security issue if callback_id can be guessed
        #       a security system with authorised callback_id must be implemented, similar to the one for authorised params
        profile = ISATSession(self.session).profile
        d = self.asyncBridgeCall("launchAction", callback_id, data, profile)
        return d

    def jsonrpc_chatStateComposing(self, to_jid_s):
        """Call the method to process a "composing" state.
        @param to_jid_s: contact the user is composing to
        """
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.chatStateComposing(to_jid_s, profile)

    def jsonrpc_getNewAccountDomain(self):
        """@return: the domain for new account creation"""
        d = self.asyncBridgeCall("getNewAccountDomain")
        return d

    def jsonrpc_confirmationAnswer(self, confirmation_id, result, answer_data):
        """Send the user's answer to any previous 'askConfirmation' signal"""
        profile = ISATSession(self.session).profile
        self.sat_host.bridge.confirmationAnswer(confirmation_id, result, answer_data, profile)

    def jsonrpc_syntaxConvert(self, text, syntax_from=Const.SYNTAX_XHTML, syntax_to=Const.SYNTAX_CURRENT):
        """ Convert a text between two syntaxes
        @param text: text to convert
        @param syntax_from: source syntax (e.g. "markdown")
        @param syntax_to: dest syntax (e.g.: "XHTML")
        @param safe: clean resulting XHTML to avoid malicious code if True (forced here)
        @return: converted text """
        profile = ISATSession(self.session).profile
        return self.sat_host.bridge.syntaxConvert(text, syntax_from, syntax_to, True, profile)


class Register(JSONRPCMethodManager):
    """This class manage the registration procedure with SàT
    It provide an api for the browser, check password and setup the web server"""

    def __init__(self, sat_host):
        JSONRPCMethodManager.__init__(self, sat_host)
        self.profiles_waiting={}
        self.request=None

    def getWaitingRequest(self, profile):
        """Tell if a profile is trying to log in"""
        if self.profiles_waiting.has_key(profile):
            return self.profiles_waiting[profile]
        else:
            return None

    def render(self, request):
        """
        Render method with some hacks:
           - if login is requested, try to login with form data
           - except login, every method is jsonrpc
           - user doesn't need to be authentified for isRegistered or registerParams, but must be for all other methods
        """
        if request.postpath==['login']:
            return self.login(request)
        _session = request.getSession()
        parsed = jsonrpclib.loads(request.content.read())
        method = parsed.get("method")
        if  method not in ['isRegistered',  'registerParams', 'getMenus']:
            #if we don't call these methods, we need to be identified
            profile = ISATSession(_session).profile
            if not profile:
                #user is not identified, we return a jsonrpc fault
                fault = jsonrpclib.Fault(Const.ERRNUM_LIBERVIA, "Not allowed") #FIXME: define some standard error codes for libervia
                return jsonrpc.JSONRPC._cbRender(self, fault, request, parsed.get('id'), parsed.get('jsonrpc'))
        self.request = request
        return jsonrpc.JSONRPC.render(self, request)

    def login(self, request):
        """
        this method is called with the POST information from the registering form
        it test if the password is ok, and log in if it's the case,
        else it return an error
        @param request: request of the register formulaire, must have "login" and "password" as arguments
        @return: A constant indicating the state:
            - BAD REQUEST: something is wrong in the request (bad arguments, profile_key for login)
            - AUTH ERROR: either the profile or the password is wrong
            - ALREADY WAITING: a request has already be made for this profile
            - server.NOT_DONE_YET: the profile is being processed, the return value will be given by self._logged or self._logginError
        """

        try:
            if request.args['submit_type'][0] == 'login':
                _login = request.args['login'][0]
                if _login.startswith('@'):
                    raise Exception('No profile_key allowed')
                _pass = request.args['login_password'][0]

            elif request.args['submit_type'][0] == 'register':
                return self._registerNewAccount(request)

            else:
                raise Exception('Unknown submit type')
        except KeyError:
            return "BAD REQUEST"

        _profile_check = self.sat_host.bridge.getProfileName(_login)

        def profile_pass_cb(_profile_pass):
            if not _profile_check or _profile_check != _login or _profile_pass != _pass:
                request.write("AUTH ERROR")
                request.finish()
                return

            if self.profiles_waiting.has_key(_login):
                request.write("ALREADY WAITING")
                request.finish()
                return

            if self.sat_host.bridge.isConnected(_login):
                request.write(self._logged(_login, request, finish=False))
                request.finish()
                return

            self.profiles_waiting[_login] = request
            d = self.asyncBridgeCall("asyncConnect", _login)
            return d

        def profile_pass_errback(ignore):
            error("INTERNAL ERROR: can't check profile password")
            request.write("AUTH ERROR")
            request.finish()

        d = self.asyncBridgeCall("asyncGetParamA", "Password", "Connection", profile_key=_login)
        d.addCallbacks(profile_pass_cb, profile_pass_errback)

        return server.NOT_DONE_YET

    def _postAccountCreation(self, answer_type, id, data, profile):
        """Called when a account has just been created,
        setup stuff has microblog access"""
        def _connected(ignore):
            mblog_d = self.asyncBridgeCall("setMicroblogAccess", "open", profile)
            mblog_d.addBoth(lambda ignore: self.sat_host.bridge.disconnect(profile))

        d = self.asyncBridgeCall("asyncConnect", profile)
        d.addCallback(_connected)

    def _registerNewAccount(self, request):
        """Create a new account, or return error
        @param request: initial login request
        @return: "REGISTRATION" in case of success"""
        #TODO: must be moved in SàT core

        try:
            profile = login = request.args['register_login'][0]
            password = request.args['register_password'][0] #FIXME: password is ignored so far
            email = request.args['email'][0]
        except KeyError:
            return "BAD REQUEST"
        if not re.match(r'^[a-z0-9_-]+$', login, re.IGNORECASE) or \
           not re.match(r'^.+@.+\..+', email, re.IGNORECASE):
            return "BAD REQUEST"

        def registered(result):
            request.write('REGISTRATION')
            request.finish()

        def registeringError(failure):
            reason = failure.value.faultString
            if reason == "ConflictError":
                request.write('ALREADY EXISTS')
            elif reason == "InternalError":
                request.write('INTERNAL')
            else:
                error('Unknown registering error: %s' % (reason,))
                request.write('Unknown error (%s)' % reason)
            request.finish()

        d = self.asyncBridgeCall("registerSatAccount", email, password, profile)
        d.addCallback(registered)
        d.addErrback(registeringError)
        return server.NOT_DONE_YET

    def __cleanWaiting(self, login):
        """Remove login from waiting queue"""
        try:
            del self.profiles_waiting[login]
        except KeyError:
            pass

    def _logged(self, profile, request, finish=True):
        """Set everything when a user just logged
        and return "LOGGED" to the requester"""
        def result(answer):
            if finish:
                request.write(answer)
                request.finish()
            else:
                return answer

        self.__cleanWaiting(profile)
        _session = request.getSession()
        sat_session = ISATSession(_session)
        if sat_session.profile:
            error (('/!\\ Session has already a profile, this should NEVER happen !'))
            return result('SESSION_ACTIVE')
        sat_session.profile = profile
        self.sat_host.prof_connected.add(profile)

        def onExpire():
            info ("Session expired (profile=%s)" % (profile,))
            try:
                #We purge the queue
                del self.sat_host.signal_handler.queue[profile]
            except KeyError:
                pass
            #and now we disconnect the profile
            self.sat_host.bridge.disconnect(profile)

        _session.notifyOnExpire(onExpire)

        d = defer.Deferred()
        return result('LOGGED')

    def _logginError(self, login, request, error_type):
        """Something went wrong during loggin, return an error"""
        self.__cleanWaiting(login)
        return error_type

    def jsonrpc_isConnected(self):
        _session = self.request.getSession()
        profile = ISATSession(_session).profile
        return self.sat_host.bridge.isConnected(profile)

    def jsonrpc_connect(self):
        _session = self.request.getSession()
        profile = ISATSession(_session).profile
        if self.profiles_waiting.has_key(profile):
            raise jsonrpclib.Fault(1,'Already waiting') #FIXME: define some standard error codes for libervia
        self.profiles_waiting[profile] = self.request
        self.sat_host.bridge.connect(profile)
        return server.NOT_DONE_YET

    def jsonrpc_isRegistered(self):
        """Tell if the user is already registered"""
        _session = self.request.getSession()
        profile = ISATSession(_session).profile
        return bool(profile)

    def jsonrpc_registerParams(self):
        """Register the frontend specific parameters"""
        params = """
        <params>
        <individual>
        <category name="%(category_name)s" label="%(category_label)s">
            <param name="%(param_name)s" label="%(param_label)s" value="false" type="bool" security="0"/>
         </category>
        </individual>
        </params>
        """ % {
            'category_name': Const.ENABLE_UNIBOX_KEY,
            'category_label': _(Const.ENABLE_UNIBOX_KEY),
            'param_name': Const.ENABLE_UNIBOX_PARAM,
            'param_label': _(Const.ENABLE_UNIBOX_PARAM)
        }

        self.sat_host.bridge.paramsRegisterApp(params, Const.SECURITY_LIMIT, Const.APP_NAME)

    def jsonrpc_getMenus(self):
        """Return the parameters XML for profile"""
        # XXX: we put this method in Register because we get menus before being logged
        return self.sat_host.bridge.getMenus('', Const.SECURITY_LIMIT)


class SignalHandler(jsonrpc.JSONRPC):

    def __init__(self, sat_host):
        Resource.__init__(self)
        self.register=None
        self.sat_host=sat_host
        self.signalDeferred = {}
        self.queue = {}

    def plugRegister(self, register):
        self.register = register

    def jsonrpc_getSignals(self):
        """Keep the connection alive until a signal is received, then send it
        @return: (signal, *signal_args)"""
        _session = self.request.getSession()
        profile = ISATSession(_session).profile
        if profile in self.queue: #if we have signals to send in queue
            if self.queue[profile]:
                return self.queue[profile].pop(0)
            else:
                #the queue is empty, we delete the profile from queue
                del self.queue[profile]
        _session.lock() #we don't want the session to expire as long as this connection is active
        def unlock(signal, profile):
            _session.unlock()
            try:
                source_defer = self.signalDeferred[profile]
                if source_defer.called and source_defer.result[0] == "disconnected":
                    info(u"[%s] disconnected" % (profile,))
                    _session.expire()
            except IndexError:
                error("Deferred result should be a tuple with fonction name first")

        self.signalDeferred[profile] = defer.Deferred()
        self.request.notifyFinish().addBoth(unlock, profile)
        return self.signalDeferred[profile]

    def getGenericCb(self, function_name):
        """Return a generic function which send all params to signalDeferred.callback
        function must have profile as last argument"""
        def genericCb(*args):
            profile = args[-1]
            if not profile in self.sat_host.prof_connected:
                return
            if profile in self.signalDeferred:
                self.signalDeferred[profile].callback((function_name,args[:-1]))
                del self.signalDeferred[profile]
            else:
                if not self.queue.has_key(profile):
                    self.queue[profile] = []
                self.queue[profile].append((function_name, args[:-1]))
        return genericCb

    def connected(self, profile):
        assert(self.register) #register must be plugged
        request = self.register.getWaitingRequest(profile)
        if request:
            self.register._logged(profile, request)

    def disconnected(self, profile):
        if not profile in self.sat_host.prof_connected:
            error("'disconnected' signal received for a not connected profile")
            return
        self.sat_host.prof_connected.remove(profile)
        if profile in self.signalDeferred:
            self.signalDeferred[profile].callback(("disconnected",))
            del self.signalDeferred[profile]
        else:
            if not self.queue.has_key(profile):
                self.queue[profile] = []
            self.queue[profile].append(("disconnected",))


    def connectionError(self, error_type, profile):
        assert(self.register) #register must be plugged
        request = self.register.getWaitingRequest(profile)
        if request: #The user is trying to log in
            if error_type == "AUTH_ERROR":
                _error_t = "AUTH ERROR"
            else:
                _error_t = "UNKNOWN"
            self.register._logginError(profile, request, _error_t)

    def render(self, request):
        """
        Render method wich reject access if user is not identified
        """
        _session = request.getSession()
        parsed = jsonrpclib.loads(request.content.read())
        profile = ISATSession(_session).profile
        if not profile:
            #user is not identified, we return a jsonrpc fault
            fault = jsonrpclib.Fault(Const.ERRNUM_LIBERVIA, "Not allowed") #FIXME: define some standard error codes for libervia
            return jsonrpc.JSONRPC._cbRender(self, fault, request, parsed.get('id'), parsed.get('jsonrpc'))
        self.request = request
        return jsonrpc.JSONRPC.render(self, request)

class UploadManager(Resource):
    """This class manage the upload of a file
    It redirect the stream to SàT core backend"""
    isLeaf = True
    NAME = 'path' #name use by the FileUpload

    def __init__(self, sat_host):
        self.sat_host=sat_host
        self.upload_dir = tempfile.mkdtemp()
        self.sat_host.addCleanup(shutil.rmtree, self.upload_dir)

    def getTmpDir(self):
        return self.upload_dir

    def _getFileName(self, request):
        """Generate unique filename for a file"""
        raise NotImplementedError

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        raise NotImplementedError

    def render(self, request):
        """
        Render method with some hacks:
           - if login is requested, try to login with form data
           - except login, every method is jsonrpc
           - user doesn't need to be authentified for isRegistered, but must be for all other methods
        """
        filename = self._getFileName(request)
        filepath = os.path.join(self.upload_dir, filename)
        #FIXME: the uploaded file is fully loaded in memory at form parsing time so far
        #       (see twisted.web.http.Request.requestReceived). A custom requestReceived should
        #       be written in the futur. In addition, it is not yet possible to get progression informations
        #       (see http://twistedmatrix.com/trac/ticket/288)

        with open(filepath,'w') as f:
            f.write(request.args[self.NAME][0])

        def finish(d):
            error = isinstance(d, Exception) or isinstance (d, Failure)
            request.write('KO' if error else 'OK')
            # TODO: would be great to re-use the original Exception class and message
            # but it is lost in the middle of the backtrace and encapsulated within
            # a DBusException instance --> extract the data from the backtrace?
            request.finish()

        d = JSONRPCMethodManager(self.sat_host).asyncBridgeCall(*self._fileWritten(request, filepath))
        d.addCallbacks(lambda d: finish(d), lambda failure: finish(failure))
        return server.NOT_DONE_YET


class UploadManagerRadioCol(UploadManager):
    NAME = 'song'

    def _getFileName(self, request):
        return "%s.ogg" % str(uuid.uuid4()) #XXX: chromium doesn't seem to play song without the .ogg extension, even with audio/ogg mime-type

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        profile = ISATSession(request.getSession()).profile
        return ("radiocolSongAdded", request.args['referee'][0], filepath, profile)


class UploadManagerAvatar(UploadManager):
    NAME = 'avatar_path'

    def _getFileName(self, request):
        return str(uuid.uuid4())

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        profile = ISATSession(request.getSession()).profile
        return ("setAvatar", filepath, profile)


class Libervia(service.Service):

    def __init__(self, port=8080):
        self._cleanup = []
        self.port = port
        root = ProtectedFile(Const.LIBERVIA_DIR)
        self.signal_handler = SignalHandler(self)
        _register = Register(self)
        _upload_radiocol = UploadManagerRadioCol(self)
        _upload_avatar = UploadManagerAvatar(self)
        self.signal_handler.plugRegister(_register)
        self.sessions = {} #key = session value = user
        self.prof_connected = set() #Profiles connected
        self.action_handler = SATActionIDHandler()
        ## bridge ##
        try:
            self.bridge=DBusBridgeFrontend()
        except BridgeExceptionNoService:
            print(u"Can't connect to SàT backend, are you sure it's launched ?")
            sys.exit(1)
        self.bridge.register("connected", self.signal_handler.connected)
        self.bridge.register("disconnected", self.signal_handler.disconnected)
        self.bridge.register("connectionError", self.signal_handler.connectionError)
        self.bridge.register("actionResult", self.action_handler.actionResultCb)
        #core
        for signal_name in ['presenceUpdate', 'newMessage', 'subscribe', 'contactDeleted', 'newContact', 'entityDataUpdated', 'askConfirmation', 'newAlert', 'paramUpdate']:
            self.bridge.register(signal_name, self.signal_handler.getGenericCb(signal_name))
        #plugins
        for signal_name in ['personalEvent', 'roomJoined', 'roomUserJoined', 'roomUserLeft', 'tarotGameStarted', 'tarotGameNew', 'tarotGameChooseContrat',
                            'tarotGameShowCards', 'tarotGameInvalidCards', 'tarotGameCardsPlayed', 'tarotGameYourTurn', 'tarotGameScore', 'tarotGamePlayers',
                            'radiocolStarted', 'radiocolPreload', 'radiocolPlay', 'radiocolNoUpload', 'radiocolUploadOk', 'radiocolSongRejected', 'radiocolPlayers',
                            'roomLeft', 'chatStateReceived']:
            self.bridge.register(signal_name, self.signal_handler.getGenericCb(signal_name), "plugin")
        self.media_dir = self.bridge.getConfig('','media_dir')
        self.local_dir = self.bridge.getConfig('','local_dir')
        root.putChild('', Redirect('libervia.html'))
        root.putChild('json_signal_api', self.signal_handler)
        root.putChild('json_api', MethodHandler(self))
        root.putChild('register_api', _register)
        root.putChild('upload_radiocol', _upload_radiocol)
        root.putChild('upload_avatar', _upload_avatar)
        root.putChild('blog', MicroBlog(self))
        root.putChild('css', ProtectedFile("server_css/"))
        root.putChild(os.path.dirname(Const.MEDIA_DIR), ProtectedFile(self.media_dir))
        root.putChild(os.path.dirname(Const.AVATARS_DIR), ProtectedFile(os.path.join(self.local_dir, Const.AVATARS_DIR)))
        root.putChild('radiocol', ProtectedFile(_upload_radiocol.getTmpDir(), defaultType="audio/ogg")) #We cheat for PoC because we know we are on the same host, so we use directly upload dir
        self.site = server.Site(root)
        self.site.sessionFactory = LiberviaSession

    def addCleanup(self, callback, *args, **kwargs):
        """Add cleaning method to call when service is stopped
        cleaning method will be called in reverse order of they insertion
        @param callback: callable to call on service stop
        @param *args: list of arguments of the callback
        @param **kwargs: list of keyword arguments of the callback"""
        self._cleanup.insert(0, (callback, args, kwargs))

    def startService(self):
        reactor.listenTCP(self.port, self.site)

    def stopService(self):
        print "launching cleaning methods"
        for callback, args, kwargs in self._cleanup:
            callback(*args, **kwargs)

    def run(self):
        reactor.run()

    def stop(self):
        reactor.stop()

registerAdapter(SATSession, server.Session, ISATSession)
application = service.Application(Const.APP_NAME)
service = Libervia()
service.setServiceParent(application)
