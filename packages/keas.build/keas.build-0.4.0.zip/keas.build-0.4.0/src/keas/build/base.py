###############################################################################
#
# Copyright 2008 by Keas, Inc., San Francisco, CA
#
###############################################################################
"""Build a release

$Id$
"""
__docformat__ = 'ReStructuredText'
import StringIO
import base64
import ConfigParser
import collections
import httplib
import logging
import optparse
import os
import pkg_resources
import subprocess
import sys
from UserDict import DictMixin
import urllib2
import urlparse

logger = logging.Logger('build')
formatter = logging.Formatter('%(levelname)s - %(message)s')

BUILD_SECTION = 'build'

def do(cmd, cwd=None, captureOutput=True):
    logger.debug('Command: ' + cmd)
    if captureOutput:
        stdout = stderr = subprocess.PIPE
    else:
        stdout = stderr = None
    p = subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr,
        shell=True, cwd=cwd)
    stdout, stderr = p.communicate()
    if stdout is None:
        stdout = "See output above"
    if stderr is None:
        stderr = "See output above"
    if p.returncode != 0:
        logger.error(u'An error occurred while running command: %s' %cmd)
        logger.error('Error Output: \n%s' % stderr)
        sys.exit(p.returncode)
    logger.debug('Output: \n%s' % stdout)
    return stdout

class SVN(object):

    user = None
    passwd = None
    forceAuth = False

    #TODO: spaces in urls+folder names???

    def __init__(self, user=None, passwd=None, forceAuth=False):
        self.user = user
        self.passwd = passwd
        self.forceAuth = forceAuth

    def _addAuth(self, command):
        auth = ''
        if self.user:
            auth = '--username %s --password %s' % (self.user, self.passwd)

            if self.forceAuth:
                auth += ' --no-auth-cache'

        command = command.replace('##__auth__##', auth)
        return command

    def info(self, url):
        command = 'svn info --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command)

    def ls(self, url):
        command = 'svn ls --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command)

    def cp(self, fromurl, tourl, comment):
        command = 'svn cp --non-interactive ##__auth__## -m "%s" %s %s' %(
            comment, fromurl, tourl)
        command = self._addAuth(command)
        do(command)

    def co(self, url, folder):
        command = 'svn co --non-interactive ##__auth__## %s %s' % (url, folder)
        command = self._addAuth(command)
        do(command)

    def ci(self, folder, comment):
        command = 'svn ci --non-interactive ##__auth__## -m "%s" %s' % (
            comment, folder)
        command = self._addAuth(command)
        do(command)

def getInput(prompt, default, useDefaults):
    if useDefaults:
        return default
    defaultStr = ''
    if default:
        defaultStr = ' [' + default + ']'
    value = raw_input(prompt + defaultStr + ': ')
    if not value:
        return default
    return value

def uploadContent(content, filename, url, username, password,
                  offline, method, headers=None):
    if offline:
        logger.info('Offline: File `%s` not uploaded.' %filename)
        return

    logger.debug('Uploading `%s` to %s' %(filename, url))
    pieces = urlparse.urlparse(url)
    Connection = httplib.HTTPConnection
    if pieces[0] == 'https':
        Connection = httplib.HTTPSConnection

    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]

    if headers is None:
        headers = {}

    headers["Authorization"] = "Basic %s" % base64string

    conn = Connection(pieces[1])
    conn.request(
        method,
        pieces[2],
        content,
        headers)

    response = conn.getresponse()
    if ((response.status != 201 and method == 'PUT')
        or response.status != 200 and method == 'POST'):
        logger.error('Error uploading file. Code: %i (%s)' %(
            response.status, response.reason))
    else:
        logger.info('File uploaded: %s' %filename)

def uploadFile(path, url, username, password, offline, method='PUT',
               headers=None):
    filename = os.path.split(path)[-1]

    uploadContent(open(path, 'r').read(),
                  filename, url+'/'+filename,
                  username, password, offline, method, headers=headers)


def guessNextVersion(version):
    pieces = pkg_resources.parse_version(version)
    newPieces = []
    for piece in pieces:
        try:
            newPieces.append(int(piece))
        except ValueError:
            break
    newPieces += [0]*(3-len(newPieces))
    newPieces[-1] += 1
    newVersion = '.'.join([str(piece) for piece in newPieces])
    logger.debug('Last Version: %s -> %s' %(version, newVersion))
    return newVersion

## {{{ http://code.activestate.com/recipes/576693/ (r6)
class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other
## end of http://code.activestate.com/recipes/576693/ }}}

class NonDestructiveRawConfigParser(ConfigParser.RawConfigParser):
    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self, dict_type=OrderedDict)

    def optionxform(self, optionstr):
        return optionstr


parser = optparse.OptionParser()
parser.add_option(
    "-c", "--config-file", action="store",
    dest="configFile", metavar="FILE",
    help="The file containing the configuration of the project.")

parser.add_option(
    "-q", "--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, no messages are displayed.")

parser.add_option(
    "-v", "--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is created.")

parser.add_option(
    "-d", "--use-defaults", action="store_true",
    dest="useDefaults", default=False,
    help="When specified, no user input is required and the defaults are used.")

parser.add_option(
    "-o", "--offline-mode", action="store_true",
    dest="offline", default=False,
    help="When set, no server commands are executed.")

parser.add_option(
    "-n", "--next-version", action="store_true",
    dest="nextVersion", default=False,
    help="When set, the system guesses the next version to generate.")

parser.add_option(
    "--force-version", action="store",
    dest="forceVersion", default="", metavar="VERSION",
    help="Force one common version through all packages and configs.")

parser.add_option(
    "--default-package-version", action="store",
    dest="defaultPackageVersion", default="", metavar="VERSION",
    help="Set a default package version for not yet released ones.")

parser.add_option(
    "--force-svnauth", action="store_true",
    dest="forceSvnAuth", default=False,
    help="Force svn authentication with svn-repos- credentials.")

parser.add_option(
    "-b", "--use-branch", action="store",
    dest="branch", metavar="BRANCH", default=None,
    help="When specified, this branch will be always used.")

parser.add_option(
    "-i", "--independent-branches", action="store_true",
    dest="independent", metavar="INDEPENDENT", default=False,
    help=("When specified, the system makes sure the last release is based "
         "on the given branch."))

parser.add_option(
    "--no-upload", action="store_true",
    dest="noUpload", default=False,
    help="When set, the generated configuration files are not uploaded.")

parser.add_option(
    "--no-branch-update", action="store_true",
    dest="noBranchUpdate", default=False,
    help=("When set, the branch is not updated with a new version after a "
         "release is created."))
