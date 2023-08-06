#!/usr/bin/env python
'''
Erst
a fuse filesystem backed by a mercurial repository
lets you view state on any given ISO8601 timestamp

cd /directory - current view
cd /directory/2014-01-06 - view at end of day Jan 6, 2014
cd /directory/2014-01-06T13:35:20 - view at 1:35pm (local) Jan 6, 2014
cd /directory/2014-01-06T13:35:20Z - view at 1:35pm (UTC) Jan 6, 2014

Copyright 2014 Eric Estabrooks

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''



import os
import re
import sys
import stat
import time
import errno
import subprocess
import argparse

import fuse
from fuse import FuseOSError

class Hg(object):
    '''simple class for handling mercurial commands'''
    def __init__(self, repo, debug=False, background=True):
        self.repo = repo
        self.debug = debug
        if not os.path.isdir(os.path.join(repo, '.hg')):
            self.__cmd('init')
        super(Hg, self).__init__()

    def __cmd(self, cmd):
        current = os.getcwd()
        if current != self.repo:
            os.chdir(self.repo)
        hg_cmd = 'hg %s' % cmd
        pid = subprocess.Popen(hg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_out, std_err) = pid.communicate()
        err = pid.wait()
        return (err, std_out, std_err)
        
    def manifest(self, revision=None, name_filter=None):
        cmd = 'manifest'
        if revision is not None:
            cmd += ' -r "%s"' % revision
        (ret, out, err) = self.__cmd(cmd)
        files = [x.strip() for x in out.split()]
        if name_filter is not None and len(name_filter) > 0:
            nf = name_filter
            files_out = set([x[len(nf)+1:].split('/')[0] for x in files if x.startswith(nf+'/')])
        else:
            files_out = files

        if self.debug:
            print "files:", files
            print "files_out:", files_out
        return files_out

    def commit(self, path):
        info = self.__cmd('commit %s -m "auto commit"' % path)
        if self.debug:
            print "commit:", info

    def add(self, path):
        info = self.__cmd('add %s' % path)
        if self.debug:
            print "add:", info

    def remove(self, path):
        info = self.__cmd('remove %s' % path)
        if self.debug:
            print "remove:", info
        return info[0]

    def update(self, revision=None):
        if revision is None:
            info = self.__cmd('update')
        else:
            info = self.__cmd('update -r "%s"' % revision)
        if self.debug:
            print "update:", info

    def rename(self, path, new_path):
        info = self.__cmd('rename %s %s' % (path, new_path))
        if self.debug:
            print "rename:", info
        return info[0]
    
class Erst(fuse.Operations):
    iso_date_re = re.compile('^/(\d{4})-(\d\d)-(\d\d)')
#    iso_dt_re = re.compile('^/(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)')
    iso_dt_re = re.compile('^/(\d{4}-\d\d-\d\d)(?:T(\d\d:\d\d:\d\dZ?))?(.*)')
#    iso_dt_re = re.compile('^/(\d{4})(?:-(\d\d)(?:-(\d\d)(?:T(\d\d)(?::(\d\d)(?::(\d\d))?)?)?)?)?')

    # list of things to ignore by ending
    __ignore = ('.swp', '.swpx', '.swo', '.swn', '.o', '~', '.hg')

    def __init__(self, root, debug=False): 
        self.hg = Hg(root, debug)
        self.hg.update()
        self.debug = debug
        self.root = root
        self.dlist = self.hg.manifest() 
        self.root_stat = os.lstat(root)
        self.current = None

    def __real_path(self, path, raise_enoent=True):
        info = Erst.iso_dt_re.split(path)
        revision = None
        for x in Erst.__ignore:
            if path.endswith(x):
                ignored = True
                break
        else:
            ignored = False

        if len(info) > 1:
            revision = "date('<%s" % info[1]
            if info[2] is not None: 
                revision += ' %s' % info[2]
            if info[3] is not None and len(info[3]) > 0:
                path = info[3]
            else:
                path = '/'
            revision += "')"
        if revision != self.current:
            self.hg.update(revision)
            self.current = revision
            self.dlist = self.hg.manifest(revision)
        real_path = os.path.join(self.root, path[1:])
        if raise_enoent and not ignored:
            if path != '/' and path[1:] not in self.dlist:
                if not os.path.isdir(real_path):
                    print "no such file or directory", path, real_path
                    raise FuseOSError(errno.ENOENT)
        return (real_path, revision, path, ignored)

    def chmod(self, path, mode):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is not None:
            raise FuseOSError(errno.EPERM)
        return os.chmod(real_path, mode)

    def mknod(self, path, mode, dev):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is not None:
            raise FuseOSError(errno.EPERM)
        return os.mknod(real_path, mode, dev)

    def unlink(self, path):
        (real_path, revision, path, ignored) = self.__real_path(path)
        path = path[1:]
        if revision is not None:
            raise FuseOSError(errno.EPERM)
        if not ignored:
            ret = self.hg.remove(path)
            if ret == 0:
                self.hg.commit(path)
        else:
            ret = os.unlink(real_path)
        return ret

    def utimens(self, path, times=None):
        (real_path, revision, path, ignored) = self.__real_path(path)
        return os.utime(real_path, times)

    def access(self, path, mode):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is None:
            if not os.access(real_path, mode):
                raise FuseOSError(errno.EACCES)
        else:
            if (mode & os.W_OK) == os.W_OK:
                raise FuseOSError(errno.EACCES)
            else:
                if not os.access(real_path, mode):
                    raise FuseOSError(errno.EACCES)

    def create(self, path, mode, fi=None):
        (real_path, revision, path, ignored) = self.__real_path(path, raise_enoent=False)
        path = path[1:]
        if revision is None:
            ret = os.open(real_path, os.O_WRONLY | os.O_CREAT, mode)
            if not ignored:
                self.hg.add(path)
                self.hg.commit(path)
                self.dlist.append(path)
            return ret
        else:
            raise FuseOSError(errno.EPERM)

    def readdir(self, path, handle):
        (real_path, revision, path, ignored) = self.__real_path(path)
        dlist = ['.', '..']
        manifest = self.hg.manifest(revision, path[1:])
        if manifest is not None:
            level = [x.split('/')[0] for x in manifest]
            dlist.extend(level)
        for f in dlist:
            yield f

    def mkdir(self, path, mode):
        (real_path, revision, path, ignored) = self.__real_path(path, raise_enoent=False)
        if revision is None:
            ret = os.mkdir(real_path, mode)
        else:
            raise FuseOSError(errno.EPERM)
    
    def rmdir(self, path):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is None:
            ret = os.rmdir(real_path)
        else:
            raise FuseOSError(errno.EPERM)

    def open(self, path, flags):
        (real_path, revision, path, ignored) = self.__real_path(path)
        ret = os.open(real_path, flags)
        return ret

    def read(self, path, size, offset, fh):
        (real_path, revision, path, ignored) = self.__real_path(path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, size)

    def write(self, path, buf, offset, fh):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is None:
            os.lseek(fh, offset, os.SEEK_SET)
            return os.write(fh, buf)
        else:
            raise FuseOSError(errno.EPERM)

    def truncate(self, path, length, fh=None):
        (real_path, revision, path, ignored) = self.__real_path(path)
        if revision is not None:
            raise FuseOSError(errno.EPERM)
        with open(real_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        (real_path, revision, path, ignored) = self.__real_path(path)
        ret = os.close(fh)
        if revision is None and not ignored:
            self.hg.commit(path[1:])
        return ret

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

    def rename(self, path, new_path):
        if self.debug:
            print "rename:", path, new_path
        (real_path, revision, path, ignored) = self.__real_path(path)
        path = path[1:]
        new_path = path[1:]
        if revision is None and not ignored:
            self.hg.rename(path, new_path)
            self.hg.commit("%s %s" % (path, new_path))
        else:
            raise FuseOSError(errno.EPERM)

    def getattr(self, path, fh=None):
        if path == '/':
            st = self.root_stat
        else:
            (real_path, revision, path, ignored) = self.__real_path(path)
            if revision is None:
                st = os.lstat(real_path)
            else:
                st = os.lstat(real_path)

        vals = dict((key, getattr(st, key)) for key in ('st_dev', 'st_ino', 'st_blksize', 'st_rdev', 'st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        return vals

    getxattr = None

def main(args):
    fuse.FUSE(Erst(args.root, args.debug), args.mountpoint, nothreads=True,
              foreground=args.foreground, debug=args.debug)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('erst.py', description='automatic versioning fuse filesystem')
    parser.add_argument('-f', '--foreground', action='store_true', help='run in foreground')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print debug info, implies running in foreground')
    parser.add_argument('-u', '--unmount', action='store_true', help='unmount the given mountpoint')
    parser.add_argument('-m', '--mountpoint', help='mount point for the filesystem')
    parser.add_argument('-r', '--root', help='directory containing the repo to mount')
   
    if len(sys.argv) == 1:
        parser.print_usage()
        exit(2)

    args = parser.parse_args()
    if args.debug:
        args.foreground = True

    if args.unmount:
        if args.mountpoint is None:
            parser.error("you must specify a mountpoint to unmount")
        ret = subprocess.call(['fusermount', '-u', args.mountpoint])
        exit(ret)
    else:
        if args.root is None or args.mountpoint is None:
            parser.error("you must specify mountpoint and root to mount an erst filesystem")

    if not args.root.startswith('/'): # get fully qualified path for root
        args.root = os.path.realpath(args.root)

    os.chdir(args.root) # switch directory to repository home
    main(args)
