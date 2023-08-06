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

typedef int32_t pid_t;
/* pid's get cached, we need a way to get at the real value */
pid_t getpid(void);
pid_t getppid(void);
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

CLONE_FS = C.CLONE_FS
CLONE_NEWNS = C.CLONE_NEWNS
CLONE_NEWUTS = C.CLONE_NEWUTS
CLONE_NEWIPC = C.CLONE_NEWIPC
CLONE_NEWUSER = C.CLONE_NEWUSER
CLONE_NEWPID = C.CLONE_NEWPID
CLONE_NEWNET = C.CLONE_NEWNET

def main():
    pass

if __name__ == "__main__":
    main()
