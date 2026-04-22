# -*- coding: utf-8 -*-
# http_handler.py
# Responsible for: stripping auth headers + sending the modified request

AUTH_HEADERS_KEYWORDS = [
    "authorization",
    "cookie",
    "x-auth-token",
    "x-access-token",
    "x-api-key",
    "x-session-token",
    "x-csrf-token",
    "token",
    "bearer",
    "x-jwt-token",
    "x-user-token",
    "session",
    "api-key",
    "x-forwarded-user",
    "x-remote-user"
]

class HttpHandler:

    def __init__(self, callbacks, helpers):
        self._callbacks = callbacks
        self._helpers = helpers

    def detect_auth_headers(self, request_str):
        """
        Scans the raw request string and returns a list
        of header lines that match known auth header names.
        """
        found = []
        lines = request_str.split("\n")

        # Skip first line (GET /path HTTP/1.1) and stop at blank line (end of headers)
        for line in lines[1:]:
            if not line.strip():
                break
            if ":" in line:
                header_name = line.split(":")[0].strip().lower()
                if header_name in AUTH_HEADERS_KEYWORDS:
                    found.append(line.strip())

        return found

    def strip_headers(self, request_str, headers_to_strip):
        """
        Removes the specified header lines from the raw request string.
        headers_to_strip: list of full header line strings e.g. ["Authorization: Bearer abc"]
        Returns the modified request as a string.
        """
        if not headers_to_strip:
            return request_str

        # Build a set of lowercase header names to strip
        names_to_strip = set()
        for h in headers_to_strip:
            if ":" in h:
                names_to_strip.add(h.split(":")[0].strip().lower())

        lines = request_str.split("\n")
        result = [lines[0]]  # Always keep the request line e.g. GET /path HTTP/1.1
        in_headers = True

        for line in lines[1:]:
            stripped_line = line.strip()

            if in_headers:
                if not stripped_line:
                    # Blank line = end of headers, start of body
                    in_headers = False
                    result.append(line)
                    continue

                if ":" in stripped_line:
                    header_name = stripped_line.split(":")[0].strip().lower()
                    if header_name in names_to_strip:
                        continue  # Drop this header line

            result.append(line)

        return "\n".join(result)

    def send_request(self, http_service, request_str):
        """
        Converts the request string to bytes and sends it.
        Returns the response as a string, or raises an exception.
        """
        request_bytes = self._helpers.stringToBytes(request_str)
        response = self._callbacks.makeHttpRequest(http_service, request_bytes)
        response_bytes = response.getResponse()

        if response_bytes:
            return self._helpers.bytesToString(response_bytes)
        else:
            return None