#!/usr/bin/env python

from cffi import FFI
ffi = FFI()
ffi.cdef("""

// bits/sched.h linux/sched.h
#define CLONE_FS      ...
#define CLONE_NEWNS   ...
#define CLONE_NEWUTS  ...
#define CLONE_NEWIPC  ...
#define CLONE_NEWUSER ...
#define CLONE_NEWPID  ...
#define CLONE_NEWNET  ...

//long clone(unsigned long flags, void *child_stack,
//           void *ptid, void *ctid, struct pt_regs *regs);

int unshare(int flags);
int setns(int fd, int nstype);

# define MS_BIND ...
# define MS_DIRSYNC ...
# define MS_MANDLOCK ...
# define MS_MOVE ...
# define MS_NOATIME ...
# define MS_NODEV ...
# define MS_NODIRATIME ...
# define MS_NOEXEC ...
# define MS_NOSUID ...
# define MS_RDONLY ...
# define MS_RELATIME ...
# define MS_REMOUNT ...
# define MS_SILENT ...
# define MS_STRICTATIME ...
# define MS_SYNCHRONOUS ...

# define MNT_FORCE ...
# define MNT_DETACH ...
# define MNT_EXPIRE ...
# define UMOUNT_NOFOLLOW ...

int mount(const char *source, const char *target,
          const char *filesystemtype, unsigned long mountflags,
          const void *data);
int umount2(const char *target, int flags);
int pivot_root(const char *new_root, const char *put_old);

int gethostname(char *name, size_t len);
int sethostname(const char *name, size_t len);


//typedef pid_t ...
/* pid's get cached, we need a way to get at the real value */
//pid_t getpid(void);
//pid_t getppid(void);
""")


C = ffi.verify("""  
#include <sched.h>
#include <sys/mount.h>
#include <unistd.h>
#include <sys/types.h>
""", libraries=[], 
ext_package='hammerhead')   # or a list of libraries to link with

CLONE_ALL = C.CLONE_NEWIPC  | \
            C.CLONE_NEWNET  | \
            C.CLONE_NEWNS   | \
            C.CLONE_NEWUTS
#            C.CLONE_NEWPID
#            C.CLONE_NEWUSER | \

unshare = C.unshare
mount = C.mount
umount = C.umount2
setns = C.setns

CLONE_FS = C.CLONE_FS
CLONE_NEWNS = C.CLONE_NEWNS
CLONE_NEWUTS = C.CLONE_NEWUTS
CLONE_NEWIPC = C.CLONE_NEWIPC
CLONE_NEWUSER = C.CLONE_NEWUSER
CLONE_NEWPID = C.CLONE_NEWPID
CLONE_NEWNET = C.CLONE_NEWNET

MS_BIND = C.MS_BIND
MS_DIRSYNC = C.MS_DIRSYNC
MS_MANDLOCK = C.MS_MANDLOCK
MS_MOVE = C.MS_MOVE
MS_NOATIME = C.MS_NOATIME
MS_NODEV = C.MS_NODEV
MS_NODIRATIME = C.MS_NODIRATIME
MS_NOEXEC = C.MS_NOEXEC
MS_NOSUID = C.MS_NOSUID
MS_RDONLY = C.MS_RDONLY
MS_RELATIME = C.MS_RELATIME
MS_REMOUNT = C.MS_REMOUNT
MS_SILENT = C.MS_SILENT
MS_STRICTATIME = C.MS_STRICTATIME
MS_SYNCHRONOUS = C.MS_SYNCHRONOUS

NULL = ffi.NULL

def sethostname(hostname):
    return C.sethostname(hostname, len(hostname))


if __name__ == "__main__":
    from subprocess import call
    from shlex import split
    import os
    
    mount_cmd = split('mount -t proc proc /proc')
    
    status = C.unshare(C.CLONE_NEWUSER)
    
    # be root instead of the 'nobody' user
    #for filename in ['/proc/self/uid_map', ]:# '/proc/self/gid_map']:
    #	with open(filename, 'a') as f:
    #		f.write('0 1000 1\n')
    
    ret = C.unshare(CLONE_ALL)
    if ret >=0:
        print 'unshared'
        pid = os.fork()
        if pid == 0:
    #		proc = call(mount_cmd)
            ret = C.mount('', '/proc', '', C.MS_REMOUNT, '')
            print ret
            print ffi.errno
            os.execl('/bin/bash', '')
        else:
            pid, status = os.wait()
            if os.WIFEXITED(status):
                print 'Process exited with return code "%d"' % os.WEXITSTATUS(status)
            else:
                print 'Process exited abnormmaly'
    else:
        print ret
        print ffi.errno
        print 'shit went bad'
