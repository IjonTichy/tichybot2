#!/usr/bin/env python3

import errno
import socket
import sys

from io import StringIO

from irc import irccommand

class IRCConnection(object):
    def __init__(self, username, nickname=None, realname=None):
        self.username   = username
        self.nickname   = nickname or username
        self.realname   = realname or username
        self.connection = None
        self.linebuffer = ""

    def connect(self, server, port=6667):
        #if self.connection is not None:
        #    self.disconnect()

        port = int(port)
        ret  = []
        self.linebuffer = ""

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.connection.connect((server, port))

        userSend = irccommand.IRCCommand("USER", [self.username, self.username, "-"], self.realname)
        nickSend = irccommand.IRCCommand("NICK", [self.nickname], "") 

        self.sendCommand(userSend)
        ret = self.connection.recv(2**16, 30)
        self.sendCommand(nickSend)

        self.connection.setblocking(False)
        return ret

    def sendCommand(self, command):
        self.sendLine(str(command))
    
    def sendLine(self, line):
        if not line.endswith("\n"): line += "\n"
        tosend = bytes(line, encoding="utf-8")

        print("Sending: {}".format(tosend))
        self.connection.send(tosend)

    def readToBuffer(self, bufsize, timeout):
        newdata = self.connection.recv(bufsize, timeout)

        newstring = newdata.decode().replace("\r\n", "\n")
        self.linebuffer += newstring

    def recvLines(self, bufsize=2**16, timeout=0):
        self.readToBuffer(bufsize, timeout)

        i = self.linebuffer.rfind("\n")
        lines, self.linebuffer = self.linebuffer[:i], self.linebuffer[i+1:]
        lines = lines.split("\n")

        return lines
