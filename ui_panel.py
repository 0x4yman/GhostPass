# -*- coding: utf-8 -*-
# ui_panel.py
# Responsible for: the entire visual tab that appears in Burp Suite

from burp import ITab
from javax.swing import (
    JPanel, JButton, JSplitPane, JScrollPane, JTextArea,
    JLabel, JTextField, JList, DefaultListModel,
    ListSelectionModel, Box, BoxLayout, JOptionPane,
    BorderFactory, SwingUtilities
)
from javax.swing.border import TitledBorder
from java.awt import BorderLayout, Dimension, Color, Font
from http_handler import HttpHandler
import threading


class AuthBypassPanel(ITab):

    def __init__(self, callbacks, helpers):
        self._callbacks = callbacks
        self._helpers = helpers
        self._http_service = None
        self._handler = HttpHandler(callbacks, helpers)
        self._setup_ui()

    def getTabCaption(self):
        return "GhostPass"

    def getUiComponent(self):
        return self._main_panel

    def _setup_ui(self):
        self._main_panel = JPanel(BorderLayout())

        #  NORTH: controls panel 
        control_panel = JPanel()
        control_panel.setLayout(BoxLayout(control_panel, BoxLayout.Y_AXIS))
        control_panel.setBorder(BorderFactory.createEmptyBorder(8, 8, 4, 8))

        # Detected headers list (auto) 
        detected_panel = JPanel(BorderLayout())
        detected_panel.setBorder(TitledBorder(
            "Detected Auth Headers (select the ones to REMOVE before sending)"
        ))
        self._header_list_model = DefaultListModel()
        self._header_list = JList(self._header_list_model)
        self._header_list.setSelectionMode(
            ListSelectionModel.MULTIPLE_INTERVAL_SELECTION
        )
        self._header_list.setFont(Font("Monospaced", Font.PLAIN, 12))
        detected_scroll = JScrollPane(self._header_list)
        detected_scroll.setPreferredSize(Dimension(0, 100))
        detected_panel.add(detected_scroll, BorderLayout.CENTER)

        # Custom header input (optional) 
        custom_panel = JPanel()
        custom_panel.setLayout(BoxLayout(custom_panel, BoxLayout.X_AXIS))
        custom_panel.setBorder(TitledBorder(
            "Optional: manually specify a header name to also strip"
        ))
        self._custom_header_field = JTextField()
        self._custom_header_field.setToolTipText(
            "Type a header name e.g.  X-Session-ID  then click Add"
        )
        add_btn = JButton("Add", actionPerformed=self._add_custom_header)
        custom_panel.add(self._custom_header_field)
        custom_panel.add(Box.createRigidArea(Dimension(6, 0)))
        custom_panel.add(add_btn)
        custom_panel.setMaximumSize(Dimension(99999, 55))

        # Send button 
        send_row = JPanel()
        self._send_btn = JButton(
            "  Send (strip selected headers)  ",
            actionPerformed=self._on_send
        )
        self._send_btn.setBackground(Color(200, 60, 60))
        self._send_btn.setForeground(Color.WHITE)
        self._send_btn.setFont(Font("SansSerif", Font.BOLD, 13))
        self._send_btn.setEnabled(False)
        send_row.add(self._send_btn)

        control_panel.add(detected_panel)
        control_panel.add(Box.createRigidArea(Dimension(0, 4)))
        control_panel.add(custom_panel)
        control_panel.add(Box.createRigidArea(Dimension(0, 4)))
        control_panel.add(send_row)

        # CENTER: request / response side by side 
        self._request_area = JTextArea()
        self._request_area.setFont(Font("Monospaced", Font.PLAIN, 12))
        self._request_area.setEditable(True)

        self._response_area = JTextArea()
        self._response_area.setFont(Font("Monospaced", Font.PLAIN, 12))
        self._response_area.setEditable(False)
        self._response_area.setBackground(Color(248, 248, 248))

        req_scroll  = JScrollPane(self._request_area)
        resp_scroll = JScrollPane(self._response_area)

        req_scroll.setBorder(TitledBorder("Request editable (you can tweak it before sending)"))
        resp_scroll.setBorder(TitledBorder("Response"))

        split = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, req_scroll, resp_scroll)
        split.setResizeWeight(0.5)
        split.setDividerSize(5)

        #  SOUTH: status bar 
        self._status = JLabel(
            "  Ready (right-click any request  'Send to GhostPass')"
        )
        self._status.setForeground(Color(70, 70, 70))
        self._status.setFont(Font("SansSerif", Font.ITALIC, 12))

        self._main_panel.add(control_panel, BorderLayout.NORTH)
        self._main_panel.add(split,         BorderLayout.CENTER)
        self._main_panel.add(self._status,  BorderLayout.SOUTH)

    # Called by the context menu 
    def load_request(self, message):
        self._http_service = message.getHttpService()
        request_str = self._helpers.bytesToString(message.getRequest())

        self._request_area.setText(request_str)
        self._response_area.setText("")
        self._header_list_model.clear()

        # Auto-detect and populate the checklist
        detected = self._handler.detect_auth_headers(request_str)
        for h in detected:
            self._header_list_model.addElement(h)

        # Pre-select all detected headers
        if self._header_list_model.size() > 0:
            self._header_list.setSelectionInterval(
                0, self._header_list_model.size() - 1
            )

        self._send_btn.setEnabled(True)
        self._status.setText(
            "  Loaded from %s — review headers to strip, then click Send"
            % self._http_service.getHost()
        )

    #  UI events 
    def _add_custom_header(self, event):
        name = self._custom_header_field.getText().strip()
        if not name:
            return

        request_str = self._request_area.getText()
        for line in request_str.split("\n"):
            if line.lower().startswith(name.lower() + ":"):
                self._header_list_model.addElement(line.strip())
                # Auto-select the newly added one too
                last = self._header_list_model.size() - 1
                self._header_list.addSelectionInterval(last, last)
                self._custom_header_field.setText("")
                return

        JOptionPane.showMessageDialog(
            self._main_panel,
            "Header '%s' was not found in the current request." % name,
            "Header Not Found",
            JOptionPane.WARNING_MESSAGE
        )

    def _on_send(self, event):
        self._send_btn.setEnabled(False)
        self._status.setText("  Sending modified request...")
        threading.Thread(target=self._do_send).start()

    def _do_send(self):
        try:
            request_str = self._request_area.getText()

            # Collect selected headers to strip
            selected_indices = self._header_list.getSelectedIndices()
            headers_to_strip = [
                self._header_list_model.getElementAt(i)
                for i in selected_indices
            ]

            # Strip headers
            modified_request = self._handler.strip_headers(request_str, headers_to_strip)

            # Send and get response
            response_str = self._handler.send_request(self._http_service, modified_request)

            def update_ui():
                if response_str:
                    self._request_area.setText(modified_request)
                    self._response_area.setText(response_str)
                    self._status.setText(
                        "  Response received — check if the endpoint is accessible without auth!"
                    )
                else:
                    self._response_area.setText("[!] No response received from server.")
                    self._status.setText("  No response — check the host/port.")
                self._send_btn.setEnabled(True)

            SwingUtilities.invokeLater(update_ui)

        except Exception as e:
            def show_err():
                self._response_area.setText("[ERROR]\n\n" + str(e))
                self._status.setText("  Error — see response panel for details.")
                self._send_btn.setEnabled(True)
            SwingUtilities.invokeLater(show_err)