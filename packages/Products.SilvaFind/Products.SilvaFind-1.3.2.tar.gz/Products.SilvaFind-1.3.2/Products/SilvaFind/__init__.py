# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.FileSystemSite.DirectoryView import registerDirectory
from Products.SilvaFind import install
from silva.core import conf as silvaconf


silvaconf.extensionName('SilvaFind')
silvaconf.extensionTitle('Silva Find')

registerDirectory('resources', globals())

