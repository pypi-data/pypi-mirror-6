#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Netius System
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Netius System.
#
# Hive Netius System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Netius System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Netius System. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import uuid
import hashlib

import email.parser

import netius.clients
import netius.servers

class RelaySMTPServer(netius.servers.SMTPServer):
    """
    Relay version of the smtp server that relays messages
    that are not considered to be local to other servers.

    The servers uses the default smtp client implementation
    to relay the messages.
    """

    def on_header_smtp(self, connection, from_l, to_l):
        netius.servers.SMTPServer.on_header_smtp(self, connection, from_l, to_l)

        # retrieves the list or remote emails for each a relay
        # operation will have to be performed as requested by
        # the current smtp specification (federation based)
        remotes = self._remotes(to_l)

        # updates the current connection with the list of remote
        # emails that have to be relayed and starts the buffer
        # that will hold the complete message for relay
        connection.remotes = remotes
        connection.relay = []

    def on_data_smtp(self, connection, data):
        netius.servers.SMTPServer.on_data_smtp(self, connection, data)

        # verifies if there're remote addresses in the current
        # connection's message and if there is adds the received
        # data to the current relay buffer that is used
        if not connection.remotes: return
        connection.relay.append(data)

    def on_message_smtp(self, connection):
        netius.servers.SMTPServer.on_message_smtp(self, connection)

        # in case there's no remotes list in the current connection
        # there's no need to proceed as no relay is required
        if not connection.remotes: return

        # joins the current relay buffer to create the full message
        # data and then removes the (non required) termination value
        # from it to avoid any possible problems with extra size
        data_s = "".join(connection.relay)
        data_s = data_s[:netius.servers.TERMINATION_SIZE * -1]

        # retrieves the list of "froms" for the connection and then
        # sends the message for relay to all of the current remotes
        froms = self._emails(connection.from_l, prefix = "from")
        self.relay(froms, connection.remotes, data_s)

    def relay(self, froms, tos, contents):
        # retrieves the first email from the froms list as this is
        # the one that is going to be used for message id generation
        # and then generates a new "temporary" message id
        first = froms[0]
        message_id = self.message_id(email = first)

        # creates a new email parser and parses the provided contents
        # as mime text and then appends the "new" message id to it
        # converting then the result into a plain text value
        parser = email.parser.Parser()
        message = parser.parsestr(contents)
        message_id = message.get("Message-ID", message_id)
        message["Message-ID"] = message_id
        contents = message.as_string()

        # generates a new smtp client for the sending of the message,
        # uses the current host for identification and then triggers
        # the message event to send the message to the target host
        smtp_client = netius.clients.SMTPClient(
            auto_close = True,
            host = self.host
        )
        smtp_client.message(froms, tos, contents)

    def message_id(self, email = "user@localhost"):
        _user, domain = email.split("@", 1)
        domain = self.host or domain
        identifier = str(uuid.uuid4())
        digest = hashlib.sha1(identifier).hexdigest()
        digest = digest.upper()
        return "<%s@%s>" % (digest, domain)

if __name__ == "__main__":
    import logging
    server = RelaySMTPServer(level = logging.DEBUG)
    server.serve(env = True)
