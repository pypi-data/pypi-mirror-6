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

import pyjd  # this is dummy in pyjs
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.HTML import HTML
from pyjamas.ui.KeyboardListener import KEY_ESCAPE
from pyjamas.Timer import Timer
from pyjamas import Window, DOM
from pyjamas.JSONService import JSONProxy

from browser_side.register import RegisterBox
from browser_side.contact import ContactPanel
from browser_side.base_widget import WidgetsPanel
from browser_side.panels import MicroblogItem
from browser_side import panels, dialog
from browser_side.jid import JID
from browser_side.xmlui import XMLUI
from browser_side.html_tools import html_sanitize
from browser_side.notification import Notification

from sat_frontends.tools.misc import InputHistory
from sat_frontends.tools.strings import getURLParams
from constants import Const
from sat.core.i18n import _


MAX_MBLOG_CACHE = 500  # Max microblog entries kept in memories

# Set to true to not create a new LiberviaWidget when a similar one
# already exist (i.e. a chat panel with the same target). Instead
# the existing widget will be eventually removed from its parent
# and added to new WidgetsPanel, or replaced to the expected
# position if the previous and the new parent are the same.
REUSE_EXISTING_LIBERVIA_WIDGETS = True


class LiberviaJsonProxy(JSONProxy):
    def __init__(self, *args, **kwargs):
        JSONProxy.__init__(self, *args, **kwargs)
        self.handler = self
        self.cb = {}
        self.eb = {}

    def call(self, method, cb, *args):
        _id = self.callMethod(method, args)
        if cb:
            if isinstance(cb, tuple):
                if len(cb) != 2:
                    print ("ERROR: tuple syntax for bridge.call is (callback, errback), aborting")
                    return
                if cb[0] is not None:
                    self.cb[_id] = cb[0]
                self.eb[_id] = cb[1]
            else:
                self.cb[_id] = cb

    def onRemoteResponse(self, response, request_info):
        if request_info.id in self.cb:
            _cb = self.cb[request_info.id]
            # if isinstance(_cb, tuple):
            #     #we have arguments attached to the callback
            #     #we send them after the answer
            #     callback, args = _cb
            #     callback(response, *args)
            # else:
            #     #No additional argument, we call directly the callback
            _cb(response)
            del self.cb[request_info.id]
            if request_info.id in self.eb:
                del self.eb[request_info.id]

    def onRemoteError(self, code, errobj, request_info):
        """def dump(obj):
            print "\n\nDUMPING %s\n\n" % obj
            for i in dir(obj):
                print "%s: %s" % (i, getattr(obj,i))"""
        if request_info.id in self.eb:
            _eb = self.eb[request_info.id]
            _eb((code, errobj))
            del self.cb[request_info.id]
            del self.eb[request_info.id]
        else:
            if code != 0:
                print ("Internal server error")
                """for o in code, error, request_info:
                    dump(o)"""
            else:
                if isinstance(errobj['message'], dict):
                    print("Error %s: %s" % (errobj['message']['faultCode'], errobj['message']['faultString']))
                else:
                    print("Error: %s" % errobj['message'])


class RegisterCall(LiberviaJsonProxy):
    def __init__(self):
        LiberviaJsonProxy.__init__(self, "/register_api",
                        ["isRegistered", "isConnected", "connect", "registerParams", "getMenus"])


class BridgeCall(LiberviaJsonProxy):
    def __init__(self):
        LiberviaJsonProxy.__init__(self, "/json_api",
                        ["getContacts", "addContact", "sendMessage", "sendMblog", "sendMblogComment",
                         "getLastMblogs", "getMassiveLastMblogs", "getMblogComments", "getProfileJid",
                         "getHistory", "getPresenceStatus", "joinMUC", "mucLeave", "getRoomsJoined",
                         "inviteMUC", "launchTarotGame", "getTarotCardsPaths", "tarotGameReady",
                         "tarotGamePlayCards", "launchRadioCollective",
                         "getWaitingSub", "subscription", "delContact", "updateContact", "getCard",
                         "getEntityData", "getParamsUI", "asyncGetParamA", "setParam", "launchAction",
                         "disconnect", "chatStateComposing", "getNewAccountDomain", "confirmationAnswer",
                         "syntaxConvert",
                        ])


class BridgeSignals(LiberviaJsonProxy):
    RETRY_BASE_DELAY = 1000

    def __init__(self, host):
        self.host = host
        self.retry_delay = self.RETRY_BASE_DELAY
        LiberviaJsonProxy.__init__(self, "/json_signal_api",
                        ["getSignals"])

    def onRemoteResponse(self, response, request_info):
        self.retry_delay = self.RETRY_BASE_DELAY
        LiberviaJsonProxy.onRemoteResponse(self, response, request_info)

    def onRemoteError(self, code, errobj, request_info):
        if errobj['message'] == 'Empty Response':
            Window.getLocation().reload()  # XXX: reset page in case of session ended.
                                           # FIXME: Should be done more properly without hard reload
        LiberviaJsonProxy.onRemoteError(self, code, errobj, request_info)
        #we now try to reconnect
        if isinstance(errobj['message'], dict) and errobj['message']['faultCode'] == 0:
            Window.alert('You are not allowed to connect to server')
        else:
            def _timerCb():
                self.host.bridge_signals.call('getSignals', self.host._getSignalsCB)
            Timer(notify=_timerCb).schedule(self.retry_delay)
            self.retry_delay *= 2


class SatWebFrontend(InputHistory):
    def onModuleLoad(self):
        print "============ onModuleLoad =============="
        panels.ChatPanel.registerClass()
        panels.MicroblogPanel.registerClass()
        self.whoami = None
        self._selected_listeners = set()
        self.bridge = BridgeCall()
        self.bridge_signals = BridgeSignals(self)
        self.uni_box = None
        self.status_panel = panels.PresenceStatusPanel(self)
        self.contact_panel = ContactPanel(self)
        self.panel = panels.MainPanel(self)
        self.discuss_panel = self.panel.discuss_panel
        self.tab_panel = self.panel.tab_panel
        self.tab_panel.addTabListener(self)
        self.libervia_widgets = set()  # keep track of all actives LiberviaWidgets
        self.room_list = []  # list of rooms
        self.mblog_cache = []  # used to keep our own blog entries in memory, to show them in new mblog panel
        self.avatars_cache = {}  # keep track of jid's avatar hash (key=jid, value=file)
        self._register_box = None
        RootPanel().add(self.panel)
        self.notification = Notification()
        DOM.addEventPreview(self)
        self._register = RegisterCall()
        self._register.call('getMenus', self.panel.menu.createMenus)
        self._register.call('registerParams', None)
        self._register.call('isRegistered', self._isRegisteredCB)
        self.initialised = False
        self.init_cache = []  # used to cache events until initialisation is done
        # define here the parameters that have an incidende to UI refresh
        self.params_ui = {"unibox": {"name": Const.ENABLE_UNIBOX_PARAM,
                                     "category": Const.ENABLE_UNIBOX_KEY,
                                     "cast": lambda value: value == 'true',
                                     "value": None
                                     }
                          }

    def addSelectedListener(self, callback):
        self._selected_listeners.add(callback)

    def getSelected(self):
        wid = self.tab_panel.getCurrentPanel()
        if not isinstance(wid, WidgetsPanel):
            print "ERROR: Tab widget is not a WidgetsPanel, can't get selected widget"
            return None
        return wid.selected

    def setSelected(self, widget):
        """Define the selected widget"""
        widgets_panel = self.tab_panel.getCurrentPanel()
        if not isinstance(widgets_panel, WidgetsPanel):
            return

        selected = widgets_panel.selected

        if selected == widget:
            return

        if selected:
            selected.removeStyleName('selected_widget')

        widgets_panel.selected = widget

        if widget:
            widgets_panel.selected.addStyleName('selected_widget')

        for callback in self._selected_listeners:
            callback(widget)

    def resize(self):
        """Resize elements"""
        Window.onResize()

    def onBeforeTabSelected(self, sender, tab_index):
        return True

    def onTabSelected(self, sender, tab_index):
        selected = self.getSelected()
        for callback in self._selected_listeners:
            callback(selected)

    def onEventPreview(self, event):
        if event.type in ["keydown", "keypress", "keyup"] and event.keyCode == KEY_ESCAPE:
            #needed to prevent request cancellation in Firefox
            event.preventDefault()
        return True

    def getAvatar(self, jid_str):
        """Return avatar of a jid if in cache, else ask for it"""
        def dataReceived(result):
            if 'avatar' in result:
                self._entityDataUpdatedCb(jid_str, 'avatar', result['avatar'])
            else:
                self.bridge.call("getCard", None, jid_str)

        def avatarError(error_data):
            # The jid is maybe not in our roster, we ask for the VCard
            self.bridge.call("getCard", None, jid_str)

        if jid_str not in self.avatars_cache:
            self.bridge.call('getEntityData', (dataReceived, avatarError), jid_str, ['avatar'])
            self.avatars_cache[jid_str] = "/media/misc/empty_avatar"
        return self.avatars_cache[jid_str]

    def registerWidget(self, wid):
        print "Registering", wid.getDebugName()
        self.libervia_widgets.add(wid)

    def unregisterWidget(self, wid):
        try:
            self.libervia_widgets.remove(wid)
        except KeyError:
            print ('WARNING: trying to remove a non registered Widget:', wid.getDebugName())

    def refresh(self):
        """Refresh the general display."""
        self.panel.refresh()
        if self.params_ui['unibox']['value']:
            self.uni_box = self.panel.unibox_panel.unibox
        else:
            self.uni_box = None
        for lib_wid in self.libervia_widgets:
            lib_wid.refresh()
        self.resize()

    def addTab(self, label, wid, select=True):
        """Create a new tab and eventually add a widget in
        @param label: label of the tab
        @param wid: LiberviaWidget to add
        @param select: True to select the added tab
        """
        widgets_panel = WidgetsPanel(self)
        self.tab_panel.add(widgets_panel, label)
        widgets_panel.addWidget(wid)
        if select:
            self.tab_panel.selectTab(self.tab_panel.getWidgetCount() - 1)
        return widgets_panel

    def addWidget(self, wid, tab_index=None):
        """ Add a widget at the bottom of the current or specified tab
        @param wid: LiberviaWidget to add
        @param tab_index: index of the tab to add the widget to"""
        if tab_index is None or tab_index < 0 or tab_index >= self.tab_panel.getWidgetCount():
            panel = self.tab_panel.getCurrentPanel()
        else:
            panel = self.tab_panel.tabBar.getTabWidget(tab_index)
        panel.addWidget(wid)

    def displayNotification(self, title, body):
        self.notification.notify(title, body)

    def _isRegisteredCB(self, registered):
        if not registered:
            self._register_box = RegisterBox(self.logged)
            self._register_box.centerBox()
            self._register_box.show()
            self._tryAutoConnect()
        else:
            self._register.call('isConnected', self._isConnectedCB)

    def _isConnectedCB(self, connected):
        if not connected:
            self._register.call('connect', lambda x: self.logged())
        else:
            self.logged()

    def logged(self):
        if self._register_box:
            self._register_box.hide()
            del self._register_box  # don't work if self._register_box is None

        #it's time to fill the page
        self.bridge.call('getContacts', self._getContactsCB)
        self.bridge.call('getParamsUI', self._getParamsUICB)
        self.bridge_signals.call('getSignals', self._getSignalsCB)
        #We want to know our own jid
        self.bridge.call('getProfileJid', self._getProfileJidCB)

        def domain_cb(value):
            self._defaultDomain = value
            print("new account domain: %s" % value)

        def domain_eb(value):
            self._defaultDomain = "libervia.org"

        self.bridge.call("getNewAccountDomain", (domain_cb, domain_eb))
        self.discuss_panel.addWidget(panels.MicroblogPanel(self, []))

        # get ui params and refresh the display
        count = 0  # used to do something similar to DeferredList

        def params_ui_cb(param, value=None):
            count += 1
            refresh = count == len(self.params_ui)
            self._paramUpdate(param['name'], value, param['category'], refresh)
        for param in self.params_ui:
            self.bridge.call('asyncGetParamA', lambda value: params_ui_cb(self.params_ui[param], value),
                             self.params_ui[param]['name'], self.params_ui[param]['category'])

    def _tryAutoConnect(self):
        """This method retrieve the eventual URL parameters to auto-connect the user."""
        params = getURLParams(Window.getLocation().getSearch())
        if "login" in params:
            self._register_box._form.login_box.setText(params["login"])
            self._register_box._form.login_pass_box.setFocus(True)
            if "passwd" in params:
                # try to connect
                self._register_box._form.login_pass_box.setText(params["passwd"])
                self._register_box._form.onLogin(None)
                return True
            else:
                # this would eventually set the browser saved password
                Timer(5, lambda: self._register_box._form.login_pass_box.setFocus(True))

    def _actionCb(self, data):
        if not data:
            # action was a one shot, nothing to do
            pass
        elif "xmlui" in data:
            ui = XMLUI(self, xml_data = data['xmlui'])
            _dialog = dialog.GenericDialog(ui.title, ui)
            ui.setCloseCb(_dialog.close)
            _dialog.setSize('80%', '80%')
            _dialog.show()
        else:
            dialog.InfoDialog("Error",
                              "Unmanaged action result", Width="400px").center()

    def _actionEb(self, err_data):
        err_code, err_obj = err_data
        dialog.InfoDialog("Error",
                          str(err_obj), Width="400px").center()

    def launchAction(self, callback_id, data):
        """ Launch a dynamic action
        @param callback_id: id of the action to launch
        @param data: data needed only for certain actions

        """
        if data is None:
            data = {}
        self.bridge.call('launchAction', (self._actionCb, self._actionEb), callback_id, data)

    def _getContactsCB(self, contacts_data):
        for contact in contacts_data:
            jid, attributes, groups = contact
            self._newContactCb(jid, attributes, groups)

    def _getSignalsCB(self, signal_data):
        self.bridge_signals.call('getSignals', self._getSignalsCB)
        print('Got signal ==> name: %s, params: %s' % (signal_data[0], signal_data[1]))
        name, args = signal_data
        if name == 'personalEvent':
            self._personalEventCb(*args)
        elif name == 'newMessage':
            self._newMessageCb(*args)
        elif name == 'presenceUpdate':
            self._presenceUpdateCb(*args)
        elif name == 'paramUpdate':
            self._paramUpdate(*args)
        elif name == 'roomJoined':
            self._roomJoinedCb(*args)
        elif name == 'roomLeft':
            self._roomLeftCb(*args)
        elif name == 'roomUserJoined':
            self._roomUserJoinedCb(*args)
        elif name == 'roomUserLeft':
            self._roomUserLeftCb(*args)
        elif name == 'askConfirmation':
            self._askConfirmation(*args)
        elif name == 'newAlert':
            self._newAlert(*args)
        elif name == 'tarotGamePlayers':
            self._tarotGameStartedCb(True, *args)
        elif name == 'tarotGameStarted':
            self._tarotGameStartedCb(False, *args)
        elif name == 'tarotGameNew' or \
             name == 'tarotGameChooseContrat' or \
             name == 'tarotGameShowCards' or \
             name == 'tarotGameInvalidCards' or \
             name == 'tarotGameCardsPlayed' or \
             name == 'tarotGameYourTurn' or \
             name == 'tarotGameScore':
            self._tarotGameGenericCb(name, args[0], args[1:])
        elif name == 'radiocolPlayers':
            self._radioColStartedCb(True, *args)
        elif name == 'radiocolStarted':
            self._radioColStartedCb(False, *args)
        elif name == 'radiocolPreload':
            self._radioColGenericCb(name, args[0], args[1:])
        elif name == 'radiocolPlay':
            self._radioColGenericCb(name, args[0], args[1:])
        elif name == 'radiocolNoUpload':
            self._radioColGenericCb(name, args[0], args[1:])
        elif name == 'radiocolUploadOk':
            self._radioColGenericCb(name, args[0], args[1:])
        elif name == 'radiocolSongRejected':
            self._radioColGenericCb(name, args[0], args[1:])
        elif name == 'subscribe':
            self._subscribeCb(*args)
        elif name == 'contactDeleted':
            self._contactDeletedCb(*args)
        elif name == 'newContact':
            self._newContactCb(*args)
        elif name == 'entityDataUpdated':
            self._entityDataUpdatedCb(*args)
        elif name == 'chatStateReceived':
            self._chatStateReceivedCb(*args)

    def _getParamsUICB(self, xmlui):
        """Hide the parameters item if there's nothing to display"""
        if not xmlui:
            self.panel.menu.removeItemParams()

    def _ownBlogsFills(self, mblogs):
        #put our own microblogs in cache, then fill all panels with them
        for publisher in mblogs:
            for mblog in mblogs[publisher]:
                if not mblog.has_key('content'):
                    print ("WARNING: No content found in microblog [%s]", mblog)
                    continue
                if mblog.has_key('groups'):
                    _groups = set(mblog['groups'].split() if mblog['groups'] else [])
                else:
                    _groups = None
                mblog_entry = MicroblogItem(mblog)
                self.mblog_cache.append((_groups, mblog_entry))

        if len(self.mblog_cache) > MAX_MBLOG_CACHE:
            del self.mblog_cache[0:len(self.mblog_cache - MAX_MBLOG_CACHE)]
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.MicroblogPanel):
                self.FillMicroblogPanel(lib_wid)
        self.initialised = True # initialisation phase is finished here
        for event_data in self.init_cache: # so we have to send all the cached events
            self._personalEventCb(*event_data)
        del self.init_cache

    def _getProfileJidCB(self, jid):
        self.whoami = JID(jid)
        #we can now ask our status
        self.bridge.call('getPresenceStatus', self._getPresenceStatusCb)
        #the rooms where we are
        self.bridge.call('getRoomsJoined', self._getRoomsJoinedCb)
        #and if there is any subscription request waiting for us
        self.bridge.call('getWaitingSub', self._getWaitingSubCb)
        #we fill the panels already here
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.MicroblogPanel):
                if lib_wid.accept_all():
                    self.bridge.call('getMassiveLastMblogs', lib_wid.massiveInsert, 'ALL', [], 10)
                else:
                    self.bridge.call('getMassiveLastMblogs', lib_wid.massiveInsert, 'GROUP', lib_wid.accepted_groups, 10)

        #we ask for our own microblogs:
        self.bridge.call('getMassiveLastMblogs', self._ownBlogsFills, 'JID', [self.whoami.bare], 10)

    ## Signals callbacks ##

    def _personalEventCb(self, sender, event_type, data):
        if not self.initialised:
            self.init_cache.append((sender, event_type, data))
            return
        sender = JID(sender).bare
        if event_type == "MICROBLOG":
            if not 'content' in data:
                print ("WARNING: No content found in microblog data")
                return
            if 'groups' in data:
                _groups = set(data['groups'].split() if data['groups'] else [])
            else:
                _groups = None
            mblog_entry = MicroblogItem(data)

            for lib_wid in self.libervia_widgets:
                if isinstance(lib_wid, panels.MicroblogPanel):
                    self.addBlogEntry(lib_wid, sender, _groups, mblog_entry)

            if sender == self.whoami.bare:
                found = False
                for index in xrange(0, len(self.mblog_cache)):
                    entry = self.mblog_cache[index]
                    if entry[1].id == mblog_entry.id:
                        # replace existing entry
                        self.mblog_cache.remove(entry)
                        self.mblog_cache.insert(index, (_groups, mblog_entry))
                        found = True
                        break
                if not found:
                    self.mblog_cache.append((_groups, mblog_entry))
                    if len(self.mblog_cache) > MAX_MBLOG_CACHE:
                        del self.mblog_cache[0:len(self.mblog_cache - MAX_MBLOG_CACHE)]
        elif event_type == 'MICROBLOG_DELETE':
            for lib_wid in self.libervia_widgets:
                if isinstance(lib_wid, panels.MicroblogPanel):
                    lib_wid.removeEntry(data['type'], data['id'])
            print self.whoami.bare, sender, data['type']
            if sender == self.whoami.bare and data['type'] == 'main_item':
                for index in xrange(0, len(self.mblog_cache)):
                    entry = self.mblog_cache[index]
                    if entry[1].id == data['id']:
                        self.mblog_cache.remove(entry)
                        break

    def addBlogEntry(self, mblog_panel, sender, _groups, mblog_entry):
        """Check if an entry can go in MicroblogPanel and add to it
        @param mblog_panel: MicroblogPanel instance
        @param sender: jid of the entry sender
        @param _groups: groups which can receive this entry
        @param mblog_entry: MicroblogItem instance"""
        if mblog_entry.type == "comment" or mblog_panel.isJidAccepted(sender) or (_groups == None and self.whoami and sender == self.whoami.bare) \
           or (_groups and _groups.intersection(mblog_panel.accepted_groups)):
            mblog_panel.addEntry(mblog_entry)

    def FillMicroblogPanel(self, mblog_panel):
        """Fill a microblog panel with entries in cache
        @param mblog_panel: MicroblogPanel instance
        """
        #XXX: only our own entries are cached
        for cache_entry in self.mblog_cache:
            _groups, mblog_entry = cache_entry
            self.addBlogEntry(mblog_panel, self.whoami.bare, *cache_entry)

    def getEntityMBlog(self, entity):
        print "geting mblog for entity [%s]" % (entity,)
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.MicroblogPanel):
                if lib_wid.isJidAccepted(entity):
                    self.bridge.call('getMassiveLastMblogs', lib_wid.massiveInsert, 'JID', [entity], 10)

    def getLiberviaWidget(self, class_, entity, ignoreOtherTabs=True):
        """Get the corresponding panel if it exists.
        @param class_: class of the panel (ChatPanel, MicroblogPanel...)
        @param entity: polymorphic parameter, see class_.matchEntity.
        @param ignoreOtherTabs: if True, the widgets that are not
        contained by the currently selected tab will be ignored
        @return: the existing widget that has been found or None."""
        selected_tab = self.tab_panel.getCurrentPanel()
        for lib_wid in self.libervia_widgets:
            parent = lib_wid.getWidgetsPanel(verbose=False)
            if parent is None or (ignoreOtherTabs and parent != selected_tab):
                # do not return a widget that is not in the currently selected tab
                continue
            if isinstance(lib_wid, class_):
                try:
                    if lib_wid.matchEntity(entity):
                        print "existing widget found: %s" % lib_wid.getDebugName()
                        return lib_wid
                except AttributeError as e:
                    e.stack_list()
                    return None
        return None

    def getOrCreateLiberviaWidget(self, class_, entity, select=True, new_tab=None):
        """Get the matching LiberviaWidget if it exists, or create a new one.
        @param class_: class of the panel (ChatPanel, MicroblogPanel...)
        @param entity: polymorphic parameter, see class_.matchEntity.
        @param select: if True, select the widget that has been found or created
        @param new_tab: if not None, a widget which is created is created in
        a new tab. In that case new_tab is a unicode to label that new tab.
        If new_tab is not None and a widget is found, no tab is created.
        @return: the newly created wigdet if REUSE_EXISTING_LIBERVIA_WIDGETS
         is set to False or if the widget has not been found, the existing
         widget that has been found otherwise."""
        lib_wid = None
        tab = None
        if REUSE_EXISTING_LIBERVIA_WIDGETS:
            lib_wid = self.getLiberviaWidget(class_, entity, new_tab is None)
        if lib_wid is None:  # create a new widget
            lib_wid = class_.createPanel(self, entity[0] if isinstance(entity, tuple) else entity)
            if new_tab is None:
                self.addWidget(lib_wid)
            else:
                tab = self.addTab(new_tab, lib_wid, False)
        else:  # reuse existing widget
            tab = lib_wid.getWidgetsPanel(verbose=False)
            if new_tab is None:
                if tab is not None:
                    tab.removeWidget(lib_wid)
                self.addWidget(lib_wid)
        if select:
            if new_tab is not None:
                self.tab_panel.selectTab(tab)
            # must be done after the widget is added,
            # for example to scroll to the bottom
            self.setSelected(lib_wid)
            lib_wid.refresh()
        return lib_wid

    def _newMessageCb(self, from_jid, msg, msg_type, to_jid, extra):
        _from = JID(from_jid)
        _to = JID(to_jid)
        other = _to if _from.bare == self.whoami.bare else _from
        lib_wid = self.getLiberviaWidget(panels.ChatPanel, other, ignoreOtherTabs=False)
        self.displayNotification(_from, msg)
        if lib_wid is not None:
            lib_wid.printMessage(_from, msg, extra)
        else:
            # The message has not been shown, we must indicate it
            self.contact_panel.setContactMessageWaiting(other.bare, True)

    def _presenceUpdateCb(self, entity, show, priority, statuses):
        entity_jid = JID(entity)
        if self.whoami and self.whoami == entity_jid:  # XXX: QnD way to get our presence/status
            self.status_panel.setPresence(show)
            if statuses:
                self.status_panel.setStatus(statuses.values()[0])
        else:
            self.contact_panel.setConnected(entity_jid.bare, entity_jid.resource, show, priority, statuses)

    def _roomJoinedCb(self, room_jid, room_nicks, user_nick):
        _target = JID(room_jid)
        if _target not in self.room_list:
            self.room_list.append(_target)
        chat_panel = panels.ChatPanel(self, _target, type_='group')
        chat_panel.setUserNick(user_nick)
        if _target.node.startswith('sat_tarot_'): #XXX: it's not really beautiful, but it works :)
            self.addTab("Tarot", chat_panel)
        elif _target.node.startswith('sat_radiocol_'):
            self.addTab("Radio collective", chat_panel)
        else:
            self.addTab(_target.node, chat_panel)
        chat_panel.setPresents(room_nicks)
        chat_panel.historyPrint()
        chat_panel.refresh()

    def _roomLeftCb(self, room_jid, room_nicks, user_nick):
        # FIXME: room_list contains JID instances so why MUST we do
        # 'remove(room_jid)' and not 'remove(JID(room_jid))' ????!!
        # This looks like a pyjamas bug --> check/report
        try:
            self.room_list.remove(room_jid)
        except KeyError:
            pass

    def _roomUserJoinedCb(self, room_jid_s, user_nick, user_data):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                lib_wid.userJoined(user_nick, user_data)

    def _roomUserLeftCb(self, room_jid_s, user_nick, user_data):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                lib_wid.userLeft(user_nick, user_data)

    def _tarotGameStartedCb(self, waiting, room_jid_s, referee, players):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                lib_wid.startGame("Tarot", waiting, referee, players)

    def _tarotGameGenericCb(self, event_name, room_jid_s, args):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                getattr(lib_wid.getGame("Tarot"), event_name)(*args)

    def _radioColStartedCb(self, waiting, room_jid_s, referee, players, queue_data):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                lib_wid.startGame("RadioCol", waiting, referee, players, queue_data)

    def _radioColGenericCb(self, event_name, room_jid_s, args):
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel) and lib_wid.type == 'group' and lib_wid.target.bare == room_jid_s:
                getattr(lib_wid.getGame("RadioCol"), event_name)(*args)

    def _getPresenceStatusCb(self, presence_data):
        for entity in presence_data:
            for resource in presence_data[entity]:
                args = presence_data[entity][resource]
                self._presenceUpdateCb("%s/%s" % (entity, resource), *args)

    def _getRoomsJoinedCb(self, room_data):
        for room in room_data:
            self._roomJoinedCb(*room)

    def _getWaitingSubCb(self, waiting_sub):
        for sub in waiting_sub:
            self._subscribeCb(waiting_sub[sub], sub)

    def _subscribeCb(self, sub_type, entity):
        if sub_type == 'subscribed':
            dialog.InfoDialog('Subscription confirmation', 'The contact <b>%s</b> has added you to his/her contact list' % html_sanitize(entity)).show()
            self.getEntityMBlog(entity)

        elif sub_type == 'unsubscribed':
            dialog.InfoDialog('Subscription refusal', 'The contact <b>%s</b> has refused to add you in his/her contact list' % html_sanitize(entity)).show()
            #TODO: remove microblogs from panels

        elif sub_type == 'subscribe':
            #The user want to subscribe to our presence
            _dialog = None
            msg = HTML('The contact <b>%s</b> want to add you in his/her contact list, do you accept ?' % html_sanitize(entity))

            def ok_cb(ignore):
                self.bridge.call('subscription', None, "subscribed", entity, '', _dialog.getSelectedGroups())
            def cancel_cb(ignore):
                self.bridge.call('subscription', None, "unsubscribed", entity, '', '')

            _dialog = dialog.GroupSelector([msg], self.contact_panel.getGroups(), [], "Add", ok_cb, cancel_cb)
            _dialog.setHTML('<b>Add contact request</b>')
            _dialog.show()

    def _contactDeletedCb(self, entity):
        self.contact_panel.removeContact(entity)

    def _newContactCb(self, contact, attributes, groups):
        self.contact_panel.updateContact(contact, attributes, groups)

    def _entityDataUpdatedCb(self, entity_jid_s, key, value):
        if key == "avatar":
            avatar = '/avatars/%s' % value

            self.avatars_cache[entity_jid_s] = avatar

            for lib_wid in self.libervia_widgets:
                if isinstance(lib_wid, panels.MicroblogPanel):
                    if lib_wid.isJidAccepted(entity_jid_s) or (self.whoami and entity_jid_s == self.whoami.bare):
                        lib_wid.updateValue('avatar', entity_jid_s, avatar)

    def _chatStateReceivedCb(self, from_jid_s, state):
        """Callback when a new chat state is received.
        @param from_jid_s: JID from the contact who sent his state
        @param state: new state
        """
        _from = JID(from_jid_s).bare if from_jid_s != "@ALL@" else from_jid_s
        for lib_wid in self.libervia_widgets:
            if isinstance(lib_wid, panels.ChatPanel):
                win_from = lib_wid.target.bare
                good_win = win_from == _from or _from == "@ALL@"
                if (good_win and lib_wid.type == 'one2one'):
                    if state:
                        lib_wid.setTitle(win_from + " (" + state + ")")
                    else:
                        lib_wid.setTitle(win_from)
                    # start to send "composing" state from now
                    lib_wid.state_machine.started = True
                elif (lib_wid.type == 'group'):
                    # TODO: chat state notification for groupchat
                    pass

    def _askConfirmation(self, confirmation_id, confirmation_type, data):
        answer_data = {}

        def confirm_cb(result):
            self.bridge.call('confirmationAnswer', None, confirmation_id, result, answer_data)

        if confirmation_type == "YES/NO":
            dialog.ConfirmDialog(confirm_cb, text=data["message"], title=data["title"]).show()

    def _newAlert(self, message, title, alert_type):
        dialog.InfoDialog(title, message).show()

    def _paramUpdate(self, name, value, category, refresh=True):
        """This is called when the paramUpdate signal is received, but also
        during initialization when the UI parameters values are retrieved.
        @param refresh: set to True to refresh the general UI
        """
        for param in self.params_ui:
            if name == self.params_ui[param]['name']:
                self.params_ui[param]['value'] = self.params_ui[param]['cast'](value)
                if refresh:
                    self.refresh()
                break

    def sendError(self, errorData):
        dialog.InfoDialog("Error while sending message",
                          "Your message can't be sent", Width="400px").center()
        print "sendError: %s" % str(errorData)

    def send(self, targets, text, extra={}):
        """Send a message to any target type.
        @param targets: list of tuples (type, entities, addr) with:
        - type in ("PUBLIC", "GROUP", "COMMENT", "STATUS" , "groupchat" , "chat")
        - entities could be a JID, a list groups, a node hash... depending the target
        - addr in ("To", "Cc", "Bcc") - ignore case
        @param text: the message content
        @param extra: options
        """
        # FIXME: too many magic strings, we should use constants instead
        addresses = []
        for target in targets:
            type_, entities, addr = target[0], target[1], 'to' if len(target) < 3 else target[2].lower()
            if type_ in ("PUBLIC", "GROUP"):
                self.bridge.call("sendMblog", None, type_, entities if type_ == "GROUP" else None, text, extra)
            elif type_ == "COMMENT":
                self.bridge.call("sendMblogComment", None, entities, text, extra)
            elif type_ == "STATUS":
                self.bridge.call('setStatus', None, self.status_panel.presence, text)
            elif type_ in ("groupchat", "chat"):
                addresses.append((addr, entities))
            else:
                print "ERROR: Unknown target type"
        if addresses:
            if len(addresses) == 1 and addresses[0][0] == 'to':
                self.bridge.call('sendMessage', (None, self.sendError), addresses[0][1], text, '', type_, extra)
            else:
                extra.update({'address': '\n'.join([('%s:%s' % entry) for entry in addresses])})
                self.bridge.call('sendMessage', (None, self.sendError), self.whoami.domain, text, '', type_, extra)

    def showWarning(self, type_=None, msg=None):
        """Display a popup information message, e.g. to notify the recipient of a message being composed.
        If type_ is None, a popup being currently displayed will be hidden.
        @type_: a type determining the CSS style to be applied (see WarningPopup.showWarning)
        @msg: message to be displayed
        """
        if not hasattr(self, "warning_popup"):
            self.warning_popup = panels.WarningPopup()
        self.warning_popup.showWarning(type_, msg)


if __name__ == '__main__':
    pyjd.setup("http://localhost:8080/libervia.html")
    app = SatWebFrontend()
    app.onModuleLoad()
    pyjd.run()
