# A Linux-only demo
#
import sys
from cffi import FFI

if not sys.platform.startswith('linux'):
    raise Exception("Linux-only demo")


ffi = FFI()
ffi.cdef("""

    typedef void DIR;
    typedef long ino_t;
    typedef long off_t;

    struct dirent {
        ino_t          d_ino;       /* inode number */
        off_t          d_off;       /* offset to the next dirent */
        unsigned short d_reclen;    /* length of this record */
        unsigned char  d_type;      /* type of file; not supported
                                       by all file system types */
        char           d_name[256]; /* filename */
    };

    int readdir_r(DIR *dirp, struct dirent *entry, struct dirent **result);
    int openat(int dirfd, const char *pathname, int flags);
    DIR *fdopendir(int fd);
    int closedir(DIR *dirp);

""")
ffi.C = ffi.dlopen(None)



def walk(basefd, path):
    print '{', path
    dirfd = ffi.C.openat(basefd, path, 0)
    if dirfd < 0:
        # error in openat()
        return
    dir = ffi.C.fdopendir(dirfd)
    dirent = ffi.new("struct dirent *")
    result = ffi.new("struct dirent **")
    while True:
        if ffi.C.readdir_r(dir, dirent, result):
            # error in readdir_r()
            break
        if result[0] == ffi.NULL:
            break
        name = ffi.string(dirent.d_name)
        print '%3d %s' % (dirent.d_type, name)
        if dirent.d_type == 4 and name != '.' and name != '..':
            walk(dirfd, name)
    ffi.C.closedir(dir)
    print '}'


walk(-1, "/tmp")
