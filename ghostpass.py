# -*- coding: utf-8 -*-
# GhostPass 

from burp import IBurpExtender, IContextMenuFactory
from javax.swing import JMenuItem
from ui_panel import AuthBypassPanel
import java.util as util


class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()

        callbacks.setExtensionName("GhostPass")

        # Build the UI tab
        self._panel = AuthBypassPanel(callbacks, self._helpers)
        callbacks.addSuiteTab(self._panel)

        # Register right-click context menu
        callbacks.registerContextMenuFactory(self)

        print("[*] GhostPass loaded!")
        print("[*] Right-click any request → 'Send to GhostPass'")

    def createMenuItems(self, invocation):
        menu_list = util.ArrayList()
        item = JMenuItem(
            "Send to GhostPass",
            actionPerformed=lambda e: self._send_to_panel(invocation)
        )
        menu_list.add(item)
        return menu_list

    def _send_to_panel(self, invocation):
        messages = invocation.getSelectedMessages()
        if messages and len(messages) > 0:
            self._panel.load_request(messages[0])
