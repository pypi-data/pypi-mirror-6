#
# Sippe Cloud
# Copyright (C) 2013  Robert Thomson
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

from vagoth.virt.exceptions import DriverException
import libvirt
import mako

class Connection(object):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None
        self.count = 0 # to support reentrant use
    def __enter__(self):
        if self.conn is None:
            self.conn = libvirt.open(self.connection_string)
        self.count += 1
    def __exit__(self, *args):
        self.count -= 1
        if self.count > 0:
            return
        if self.conn != None:
            self.conn.close()
        self.conn = None

class LibvirtDriver(object):
    def __init__(self, manager, local_config):
        self.config = local_config
    def provision(self, node, vm):
        pass
    def define(self, node, vm):
        pass
    def undefine(self, node, vm):
        pass
    def deprovision(self, node, vm):
        pass
    def start(self, node, vm):
        pass
    def reboot(self, node, vm):
        pass
    def stop(self, node, vm):
        pass
    def shutdown(self, node, vm):
        pass
    def info(self, node, vm):
        pass
    def status(self, node, vm):
        pass
    def migrate(self, node, vm):
        pass
