from setuptools import setup, find_packages
import sys, os

from UserString import UserString

versioneer = None
def _initialize_versioneer():
      global versioneer

      if versioneer is None:
            import versioneer

            versioneer.versionfile_source = 'upstart/_version.py'
            versioneer.versionfile_build = 'upstart/_version.py'
            versioneer.tag_prefix = ''
            versioneer.parentdir_prefix = 'upstart-'

class _VLazyVersion(UserString):
      """Wait to determine the version until someone actually casts us or 
      applies us, after our whole project has been staged.
      """

      def __init__(self, initial=''):
            self.data = initial

      def __init_version(self):
            try:
                  self.__is_loaded
            except AttributeError:
                  _initialize_versioneer()
                  self.data = versioneer.get_version()
                  self.__is_loaded = True

      def __str__(self):
            self.__init_version()

            return self.data

class _VLazyCmdClass(object):
      """Wait to determine the cmdclass until someone actually requests a 
      particular class, at which point we proxy the request to the actual 
      dictionary.
      """

      def __init__(self):
            self.__is_loaded = False

      def __init_cmdclass(self):
            if self.__is_loaded is False:
                  _initialize_versioneer()
                  self.__cmdclass = versioneer.get_cmdclass()
                  self.__is_loaded = True

      def __getattr__(self, name):
            """Proxy all requests through to the standard dictionary object. 
            The first time we're called, load ourselves with the Versioneer 
            cmdclass entries.
            """

            self.__init_cmdclass()
            return getattr(self.__cmdclass, name)

      def __repr__(self):
            self.__init_cmdclass()
            return repr(self.__cmdclass)

      def __str__(self):
            self.__init_cmdclass()
            return str(self.__cmdclass)

      def __iter__(self):
            self.__init_cmdclass()
            return iter(self.__cmdclass.items())

      def __setitem__(self, k, v):
            self.__init_cmdclass()
            self.__cmdclass[k] = v

long_description=\
"An intuitive library interface to Upstart for service and job management. "\
"Requires the python-dbus Ubuntu package or equivalent."

setup(name='upstart',
      version=_VLazyVersion(), #versioneer.get_version(),
      description="Upstart-based service management.",
      long_description=long_description,
      classifiers=[],
      keywords='upstart dbus',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/PythonUpstart',
      license='GPL 2',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points="",
      cmdclass=_VLazyCmdClass()
#      cmdclass=versioneer.get_cmdclass(),
)
