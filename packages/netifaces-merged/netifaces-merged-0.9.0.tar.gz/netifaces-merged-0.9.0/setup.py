import os
import pickle
import sys
from distutils.errors import *
from textwrap import dedent

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

__version__ = "0.9.0"

# Disable hard links, otherwise building distributions fails on OS X
try:
    del os.link
except:
    pass

libraries = []
def_macros = [('NETIFACES_VERSION', __version__)]

# On Windows, we need ws2_32 and iphlpapi
if os.name == "nt":
    libraries = ['ws2_32', 'iphlpapi']
    def_macros.insert(0, ('WIN32', 1))
elif sys.platform.startswith("sunos"):
    libraries += ['socket', 'nsl']

#
#  There must be a better way to do this...
#
class my_build_ext(build_ext):
    def build_extensions(self):
        self.check_requirements()
        build_ext.build_extensions(self)

    def test_build(self, contents, link=True, execute=False, libraries=None,
                   include_dirs=None, library_dirs=None):
        name = os.path.join(self.build_temp, 'conftest-%s.c' % self.conftestidx)
        self.conftestidx += 1
        if os.path.exists(name):
            os.unlink(name)

        thefile = open(name, 'w')
        thefile.write(contents)
        thefile.close()

        sys.stdout.flush()
        sys.stderr.flush()
        mystdout = os.dup(1)
        mystderr = os.dup(2)
        result = True
        try:
            os.dup2(self.ctout, 1)
            os.dup2(self.ctout, 2)
            try:
                objects = self.compiler.compile([name],
                                                output_dir=self.build_temp,
                                                include_dirs=include_dirs,
                                                debug=self.debug)
                if link:
                    self.compiler.link_executable(objects,
                                                  'conftest',
                                                  output_dir=self.build_temp,
                                                  library_dirs=library_dirs,
                                                  libraries=libraries,
                                                  debug=self.debug)
                    if execute:
                        abspath = os.path.abspath(os.path.join(self.build_temp,
                                                               'conftest'))
                        pipe = os.popen(abspath, 'r')
                        result = pipe.read().strip()
                        status = pipe.close()
                        if status is None:
                            status = 0
                        if result == '':
                            result = True
                        if status != 0:
                            result = False

            finally:
                os.dup2(mystdout, 1)
                os.dup2(mystderr, 2)
        except CompileError:
            return False
        except DistutilsExecError:
            return False
        return result

    def check_requirements(self):
        # Load the cached config data from a previous run if possible; compiling
        # things to test for features is slow
        cache_file = os.path.join(self.build_temp, 'config.cache')
        if os.path.exists(cache_file):
            myfile = open(cache_file, 'rb')
            try:
                results = pickle.load(myfile)
            finally:
                myfile.close()
        else:
            results = {}

        self.conftestidx = 0

        sys.stdout.write("checking for getifaddrs...")

        result = results.get('have_getifaddrs', None)
        if result is not None:
            cached = '(cached)'
        else:
            cached = ''

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            outname = os.path.join(self.build_temp, 'conftest.out')
            self.ctout = os.open(outname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            testrig = dedent("""
            #include <sys/types.h>
            #include <sys/socket.h>
            #include <ifaddrs.h>
            int main(void) {
              struct ifaddrs *addrs;
              int ret;
              ret = getifaddrs(&addrs);
              freeifaddrs (addrs);
              return 0;
            }
            """)
            if self.test_build(testrig):
                result = True
            else:
                result = False

        if result:
            sys.stdout.write("found. %s" % cached + os.linesep)
            self.compiler.define_macro('HAVE_GETIFADDRS', 1)
        else:
            sys.stdout.write("not found. %s" % cached + os.linesep)

        results['have_getifaddrs'] = result

        sys.stdout.write("checking for getnameinfo...")

        result = results.get('have_getnameinfo', None)
        if result is not None:
            cached = '(cached)'
        else:
            cached = ''

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            outname = os.path.join(self.build_temp, 'conftest2.out')
            self.ctout = os.open(outname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            testrig = dedent("""
            #include <sys/types.h>
            #include <sys/socket.h>
            #include <arpa/inet.h>
            #include <netdb.h>
            #include <stdlib.h>
            int main(void) {
              struct sockaddr_in sin;
              char buffer[256];
              int ret;

              sin.sin_family = AF_INET;
              sin.sin_port = 0;
              sin.sin_addr.s_addr = htonl (INADDR_LOOPBACK);
              
              ret = getnameinfo ((struct sockaddr *)&sin, sizeof (sin),
                                 buffer, sizeof (buffer),
                                 NULL, 0,
                                 NI_NUMERICHOST);

              return 0;
            }
            """)
            if self.test_build(testrig,libraries=libraries):
                result = True
            else:
                result = False

        if result:
            sys.stdout.write("found. %s" % cached + os.linesep)
            self.compiler.define_macro('HAVE_GETNAMEINFO', 1)
        else:
            sys.stdout.write("not found. %s" % cached + os.linesep)

        results['have_getnameinfo'] = result

        if not results['have_getifaddrs']:
            sys.stdout.write("checking for socket IOCTLs...")

            result = results.get('have_socket_ioctls', None)
            if result is not None:
                cached = '(cached)'
            else:
                cached = ''

                if not os.path.exists(self.build_temp):
                    os.makedirs(self.build_temp)
                outname = os.path.join(self.build_temp, 'conftest3.out')
                self.ctout = os.open(
                    outname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)

                result = []
                ioctls = ('SIOCGIFCONF',
                          'SIOCGSIZIFCONF',
                          'SIOCGIFHWADDR',
                          'SIOCGIFADDR',
                          'SIOCGIFFLAGS',
                          'SIOCGIFDSTADDR',
                          'SIOCGIFBRDADDR',
                          'SIOCGIFNETMASK',
                          'SIOCGLIFNUM',
                          'SIOCGLIFCONF',
                          'SIOCGLIFFLAGS')
                added_includes = ''
                if sys.platform.startswith("sunos"):
                    added_includes = dedent("""
                     #include <unistd.h>
                     #include <stropts.h>
                     #include <sys/sockio.h>
                    """)

                for ioctl in ioctls:
                    testrig = dedent("""
                    #include <sys/types.h>
                    #include <sys/socket.h>
                    #include <sys/ioctl.h>
                    #include <net/if.h>
                    #include <netinet/in.h>
                    #include <arpa/inet.h>
                    %(addedinc)s
                    int main(void) {
                        int fd = socket (AF_INET, SOCK_DGRAM, IPPROTO_IP);
                        struct ifreq ifreq;

                        ioctl(fd, %(ioctl)s, &ifreq);

                        return 0;
                    }
                    """) % {"ioctl": ioctl, "addedinc": added_includes}

                    if self.test_build(testrig,libraries=libraries):
                        result.append(ioctl)

            if result:
                sys.stdout.write("%r. %s" % (result, cached) + os.linesep)
                for ioctl in result:
                    self.compiler.define_macro('HAVE_%s' % ioctl, 1)
                self.compiler.define_macro('HAVE_SOCKET_IOCTLS', 1)
            else:
                sys.stdout.write("not found. %s" % cached + os.linesep)

            results['have_socket_ioctls'] = result

        sys.stdout.write("checking for optional header files...")

        result = results.get('have_headers', None)
        if result is not None:
            cached = '(cached)'
        else:
            cached = ''

            result =[]
            headers = ('net/if_dl.h', 'netash/ash.h',
                       'netatalk/at.h', 'netax25/ax25.h',
                       'neteconet/ec.h', 'netipx/ipx.h',
                       'netpacket/packet.h', 'netrose/rose.h',
                       'linux/irda.h', 'linux/atm.h',
                       'linux/llc.h', 'linux/tipc.h',
                       'linux/dn.h')

            for header in headers:
                testrig = dedent("""
                #include <sys/types.h>
                #include <sys/socket.h>
                #include <net/if.h>
                #include <%s>
                int main (void) { return 0; }
                """ % header)

                if self.test_build(testrig, link=False):
                    result.append(header)

        if result:
            sys.stdout.write("%s. %s" % (" ".join(result), cached) + os.linesep)
            for header in result:
                macro = header.upper().replace('.', '_').replace('/', '_')
                self.compiler.define_macro('HAVE_%s' % macro, 1)
        else:
            sys.stdout.write("none found. %s" % cached + os.linesep)

        optional_headers = result
        results['have_headers'] = result

        sys.stdout.write(
            "checking whether struct sockaddr has a length field...")

        result = results.get('have_sockaddr_sa_len', None)
        if result is not None:
            cached = '(cached)'
        else:
            cached = ''

            testrig = dedent("""
            #include <sys/types.h>
            #include <sys/socket.h>
            #include <net/if.h>

            int main (void) {
              struct sockaddr sa;
              sa.sa_len = 5;
              return 0;
            }
            """)

            result = self.test_build(testrig)

        if result:
            sys.stdout.write("yes. %s" % cached + os.linesep)
            self.compiler.define_macro('HAVE_SOCKADDR_SA_LEN', 1)
        else:
            sys.stdout.write("no. %s" % cached + os.linesep)

        results['have_sockaddr_sa_len'] = result

        if not results['have_sockaddr_sa_len']:
            # GAK! On certain stupid platforms (Linux), there's no sa_len.
            # Macho Linux programmers apparently think that it's not needed,
            # however, unfortunately, getifaddrs() doesn't return the
            # lengths, because they're in the sa_len field on just about
            # everything but Linux.
            sys.stdout.write(
                "checking which sockaddr_xxx structs are defined...")
            
            result = results.get('have_sockaddrs', None)
            if result is not None:
                cached = '(cached)'
            else:
                cached = ''

                if not os.path.exists(self.build_temp):
                    os.makedirs(self.build_temp)
                outname = os.path.join(self.build_temp, 'conftest4.out')
                self.ctout = os.open(
                    outname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)

                sockaddrs = ('at', 'ax25', 'dl', 'eon', 'in', 'in6',
                             'inarp', 'ipx', 'iso', 'ns', 'un', 'x25',
                             'rose', 'ash', 'ec', 'll', 'atmpvc', 'atmsvc',
                             'dn', 'irda', 'llc')
                result = []
                for sockaddr in sockaddrs:
                    testrig = dedent("""
                    #include <sys/types.h>
                    #include <sys/socket.h>
                    #include <sys/un.h>
                    #include <net/if.h>
                    #include <netinet/in.h>
                    %(includes)s

                    int main (void) {
                      struct sockaddr_%(sockaddr)s sa;
                      return 0;
                    }
                    """) % { 'includes': os.linesep.join(
                        ['#include <%s>' % header
                         for header in optional_headers]),
                            'sockaddr': sockaddr }

                    if self.test_build(testrig):
                        result.append(sockaddr)

            if result:
                sys.stdout.write(
                    "%s. %s" % (" ".join(result), cached) + os.linesep)
                for sockaddr in result:
                    self.compiler.define_macro('HAVE_SOCKADDR_%s' \
                                               % sockaddr.upper(), 1)
            else:
                sys.stdout.write("none! %s" % cached + os.linesep)

            results['have_sockaddrs'] = result

       # Save the results to our config.cache file
        myfile = open(cache_file, 'wb')
        try:
            pickle.dump(results, myfile)
        finally:
            myfile.close()

# Don't bother detecting socket ioctls on Windows
if os.name != "nt":
    setuptools.command.build_ext.build_ext = my_build_ext

try:
    dirname = os.path.abspath(os.path.dirname(__file__))
    readme_filepath = os.path.join(dirname, "README.rst")
except NameError:
    readme_filepath = "README.rst"

if os.path.isfile(readme_filepath):
    long_description = open(readme_filepath, "r").read()
else:
    long_description = ""

setup(name='netifaces-merged',
      version=__version__,
      zip_safe=True,
      description="Portable network interface information.",
      license="MIT License",
      long_description=long_description,
      author="Oliver Palmer",
      author_email="opalmer@opalmer.com",
      url="https://github.com/opalmer/netifaces-merged",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: System :: Networking',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3'],
      ext_modules=[
          Extension(
              "netifaces", sources=["netifaces.c"],
              libraries=libraries, define_macros=def_macros)])
