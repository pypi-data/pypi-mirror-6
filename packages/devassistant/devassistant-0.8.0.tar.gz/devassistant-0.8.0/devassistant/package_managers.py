# -*- coding: utf-8 -*-
"""General notes on dependency installation:
The only class that should be used from outside is DependencyInstaller. It uses PackageManager
subclasses to install dependencies collected from assistants/snippets, e.g.
[{'rpm': ['package1', 'package2'], 'pip': ['spam']}, {'gem': ['foo']}]

DevAssistant distinguishes two general types of dependencies:
- system dependencies (rpm, pacman, ...)
- non-system dependencies

System dependencies are special, since DependencyInstaller throws away all system
dependencies that are not native to this system. E.g. it throws away RPM deps on
ArchLinux. Non-system dependencies are always processed, since they should be
distro-agnostic.

PackageManager subclasses represent the tools that are used to install the dependencies.
Note, that sometimes there isn't 1:1 mapping from dependency types to package managers -
RPM, for example, is handled by YUM on Fedora, but there are different tools
on other platforms, e.g. Zypper on OpenSuse. PackageManager subclasses should always
represent these high-level tools like YUM or Zypper, not RPM itself.
"""
from __future__ import print_function
import collections
import math
import sys
import tempfile
import threading

from devassistant import current_run
from devassistant.command_helpers import ClHelper, DialogHelper
from devassistant.logger import logger
from devassistant import exceptions
from devassistant import utils
from devassistant import settings

# mapping of dependency types to managers that handle them
# e.g. {'rpm': [YUMPackageManager, DNFPackageManager],
#       'pip': [PIPPackageManager]}
managers = {}

def register_manager(manager):
    managers.setdefault(manager.shortcut, [])
    managers[manager.shortcut].append(manager)
    return manager

class PackageManager(object):
    """Abstract class for API definition of package managers."""

    # Indicates whether this is a system manager.
    is_system = True

    @classmethod
    def get_perm_prompt(cls, package_list):
        """
        Return text for prompt (do you want to install...), to install given packages.
        """
        if cls == PackageManager:
            raise NotImplementedError()
        ln = len(package_list)
        plural = 's' if ln > 1 else ''
        return cls.permission_prompt.format(num=ln, plural=plural)

    @classmethod
    def install(cls, *args, **kwargs):
        """Install dependency.

        Note: if you want your dependency installation to be uninterruptible, pass
        ignore_sigint=True to ClHelper.run_command.
        """
        raise NotImplementedError()

    @classmethod
    def works(cls, *args, **kwargs):
        """Returns True if this package manager is usable, False otherwise."""
        raise NotImplementedError()

    @classmethod
    def is_pkg_installed(cls, *args, **kwargs):
        """Is a package managed by this manager installed?"""
        raise NotImplementedError()

    @classmethod
    def resolve(cls, *args, **kwargs):
        """
        Return all dependencies which will be installed. Problem here is that
        not all package managers could support this.
        """
        raise NotImplementedError()

    @classmethod
    def get_distro_dependencies(cls, smgr_sc):
        """
        Return dependencies needed for this non-system manager to work.
        Args:
            smgr_sc: shortcut of system manager to return dependencies for
        Returns:
            list of dependencies that are to be installed via given system dependency manager
            in order for this manager to work
        Raises:
            NotImplementedError: if this manager is system manager (makes no sense to call this)
        """
        raise NotImplementedError()


@register_manager
class YUMPackageManager(PackageManager):
    """Package manager for managing rpm packages from repositories by Yum.
    TODO: when we start using another RPM platform with another installer (OpenSuse),
    we will need to pull out the RPM stuff into common superclass."""
    permission_prompt = "Installing {num} RPM package{plural} by Yum. Is this ok?"
    shortcut = 'rpm'

    c_rpm = 'rpm'
    c_yum = 'yum'

    @classmethod
    def rpm_q(cls, rpm_name):
        try:
            # if we install by e.g. virtual provide, then rpm -q foo will fail
            # therefore we always use rpm -q --whatprovides foo
            return ClHelper.run_command(' '.join([cls.c_rpm,
                                                  '-q',
                                                  '--whatprovides',
                                                  '"' + rpm_name.strip() + '"']))
        except exceptions.ClException:
            return False

    @classmethod
    def is_rpm_installed(cls, rpm_name):
        logger.info('Checking for presence of {0}...'.format(rpm_name), extra={'event_type': 'dep_check'})

        found_rpm = cls.rpm_q(rpm_name)
        if found_rpm:
            logger.info('Found {0}'.format(found_rpm), extra={'event_type': 'dep_found'})
        else:
            logger.info('Not found, will install', extra={'event_type': 'dep_not_found'})
        return found_rpm

    @classmethod
    def is_group_installed(cls, group):
        logger.info('Checking for presence of group {0}...'.format(group))

        output = ClHelper.run_command(' '.join(
            [cls.c_yum, 'group', 'list', '"{0}"'.format(group)]))
        if 'Installed Groups' in output:
            logger.info('Found {0}'.format(group), extra={'event_type': 'dep_found'})
            return group
        else:
            logger.info('Not found, will install', extra={'event_type': 'dep_not_found'})
        return False

    @classmethod
    def was_rpm_installed(cls, rpm_name):
        # TODO: handle failure
        found_rpm = cls.rpm_q(rpm_name)
        logger.info('Installed {0}'.format(found_rpm), extra={'event_type': 'dep_installed'})
        return found_rpm

    @classmethod
    def install(cls, *args):
        cmd = ['pkexec', cls.c_yum, '-y', 'install']
        quoted_pkgs = map(lambda pkg: '"{pkg}"'.format(pkg=pkg), args)
        cmd.extend(quoted_pkgs)
        try:
            ClHelper.run_command(' '.join(cmd), ignore_sigint=True)
            return args
        except exceptions.ClException:
            return False

    @classmethod
    def works(cls):
        try:
            import yum
            return True
        except ImportError:
            return False

    @classmethod
    def is_pkg_installed(cls, pkg):
        return cls.is_group_installed(pkg) if pkg.startswith('@') else cls.is_rpm_installed(pkg)

    @classmethod
    def resolve(cls, *args):
        logger.info('Resolving RPM dependencies ...')
        import yum
        y = yum.YumBase()
        y.setCacheDir(tempfile.mkdtemp())
        for pkg in args:
            if pkg.startswith('@'):
                y.selectGroup(pkg[1:])
            else:
                try:
                    y.install(y.returnPackageByDep(pkg))
                except yum.Errors.YumBaseError:
                    msg = 'Package not found: {pkg}'.format(pkg=pkg)
                    raise exceptions.DependencyException(msg)
        y.resolveDeps()
        logger.debug('Installing/Updating:')
        to_install = []
        for pkg in y.tsInfo.getMembers():
            to_install.append(pkg.po.ui_envra)
            logger.debug(pkg.po.ui_envra)

        return to_install

    def __str__(self):
        return "rpm package manager"


@register_manager
class PacmanPackageManager(PackageManager):
    """Package manager for managing Arch Linux packages by pacman."""
    permission_prompt = "Installing {num} package{plural} by Pacman. Is this ok?"
    shortcut = 'pacman'

    c_pacman = 'pacman'

    @classmethod
    def install(cls, *args):
        cmd = ['pkexec', cls.c_pacman, '-S', '--noconfirm']
        quoted_pkgs = map(lambda pkg: '"{pkg}"'.format(pkg=pkg), args)
        cmd.extend(quoted_pkgs)
        try:
            ClHelper.run_command(' '.join(cmd), ignore_sigint=True)
            return args
        except exceptions.ClException:
            return False

    @classmethod
    def is_pacmanpkg_installed(cls, pkg_name):
        logger.info('Checking for presence of {0}...'.format(pkg_name), extra={'event_type': 'dep_check'})

        try:
            found_pkg = ClHelper.run_command('{pacman} -Q "{pkg}"'.\
                                             format(pacman=cls.c_pacman, pkg=pkg_name))
            logger.info('Found {0}'.format(found_pkg), extra={'event_type': 'dep_found'})
            return found_pkg
        except exceptions.ClException:
            logger.info('Not found, will install', extra={'event_type': 'dep_not_found'})
            return False

    @classmethod
    def is_group_installed(cls, group):
        logger.info('Checking for presence of group {0}...'.format(group))

        try:
            output = ClHelper.run_command('{pacman} -Qg "{group}"'.\
                                          format(pacman=cls.c_pacman,
                                                 group=group))
            return group
        except exceptions.ClException:
            return False

    @classmethod
    def works(cls):
        try:
            ClHelper.run_command('which pacman')
            return True
        except exceptions.ClException:
            return False

    @classmethod
    def is_pkg_installed(cls, pkg):
        return cls.is_pacmanpkg_installed(pkg) or cls.is_group_installed(pkg)

    @classmethod
    def resolve(cls, *args):
        # TODO: I currently see no way how to just resolve dependencies by pacman
        return args


@register_manager
class PIPPackageManager(PackageManager):
    """ Package manager for managing python dependencies from PyPI """
    permission_prompt = "Installing {num} package{plural} from PyPI. Is this ok?"
    shortcut = 'pip'
    is_system = False

    c_pip = 'pip'

    @classmethod
    def install(cls, *args):
        cmd = [cls.c_pip, 'install', '--user']
        quoted_pkgs = map(lambda pkg: '"{pkg}"'.format(pkg=pkg), args)
        cmd.extend(quoted_pkgs)
        try:
            ClHelper.run_command(' '.join(cmd), ignore_sigint=True)
            return args
        except exceptions.ClException:
            return False

    @classmethod
    def works(cls):
        try:
            ClHelper.run_command('pip')
            return True
        except exceptions.ClException:
            return False

    @classmethod
    def is_pkg_installed(cls, dep):
        logger.info('Checking for presence of {0}...'.format(dep),
                    extra={'event_type': 'dep_check'})
        if not getattr(cls, '_installed', None):
            query = ClHelper.run_command(' '.join([cls.c_pip, 'list']))
            cls._installed = query.split('\n')
        search = filter(lambda e: e.startswith(dep + ' '), cls._installed)
        if search:
            logger.info('Found {0}'.format(search[0]), extra={'event_type': 'dep_found'})
        else:
            logger.info('Not found, will install', extra={'event_type': 'dep_not_found'})

        return len(search) > 0

    @classmethod
    def resolve(cls, *dep):
        # depresolver for PyPI is infeasable to do -- there are no structured
        # metadata for python packages; so just return this dependency
        # PIPHelper.resolve(dep)
        logger.info('Resolving PyPI dependencies...')
        return dep

    @classmethod
    def get_distro_dependencies(self, smgr_sc):
        return ['python-pip']

    def __str__(self):
        return "pip package manager"

@register_manager
class NPMPackageManager(PackageManager):
    """ Package manager for managing python dependencies from NPM """
    permission_prompt = "Installing {num} package{plural} from NPM. Is this ok?"
    shortcut = 'npm'
    is_system = False

    c_npm = 'npm'

    @classmethod
    def install(cls, *args):
        cmd = [cls.c_npm, 'install']
        quoted_pkgs = map(lambda pkg: '"{pkg}"'.format(pkg=pkg), args)
        cmd.extend(quoted_pkgs)
        try:
            ClHelper.run_command(' '.join(cmd), ignore_sigint=True)
            return args
        except exceptions.ClException:
            return False

    @classmethod
    def works(cls):
        try:
            ClHelper.run_command('npm')
            return True
        except exceptions.ClException as e:
            return False

    @classmethod
    def is_pkg_installed(cls, dep):
        logger.info('Checking for presence of {0}...'.format(dep),
                    extra={'event_type': 'dep_check'})
        if not getattr(cls, '_installed', None):
            query = ClHelper.run_command(' '.join([cls.c_npm, 'list']))
            cls._installed = query.split('\n')
        search = filter(lambda e: e.startswith(dep + ' '), cls._installed)
        if search:
            logger.info('Found {0}'.format(search[0]), extra={'event_type': 'dep_found'})
        else:
            logger.info('Not found, will install', extra={'event_type': 'dep_not_found'})

        return len(search) > 0

    @classmethod
    def resolve(cls, *dep):
        logger.info('Resolving NPM dependencies...')
        return dep

    @classmethod
    def get_distro_dependencies(self, smgr_sc):
        return ['npm']

    def __str__(self):
        return "npm package manager"


class DependencyInstaller(object):
    """Installs all dependencies given to install() like this:
    - Calls _process_dependency for each dependency type, system dependencies always go first
      - "Implodes" the dependencies - e.g. if more 'rpm' lists were given, it creates one
        list of all of them
      - If it encounters system dependencies native for another system, it throws them away
      - For non-system dependency type (e.g. 'gem', 'pip'), it also adds a system dependency
        that has the ability to install these (e.g. rubygems, python-pip)
    - Calls _install_dependencies
      - For each dependency type
        - Gets proper manager to install it
        - Resolves dependencies of those dependencies :)
        - Installs the dependencies
    """
    # True if devassistant is installing dependencies and we can't interrupt the process
    install_lock = False

    """Class for installing dependencies """
    def __init__(self):
        # {package_manager_shorcut: ['list', 'of', 'dependencies']}
        # we're using ordered dict to preserve the order that is used in
        # assistants; we also want system dependencies to always go first
        self.dependencies = collections.OrderedDict()

    def get_package_manager(self, dep_t):
        """Choose proper package manager and return it."""
        mgrs = managers.get(dep_t, [])
        for manager in mgrs:
            if manager.works():
                return manager
        if not mgrs:
            err = 'No package manager for dependency type "{dep_t}"'.format(dep_t=dep_t)
            raise exceptions.NoPackageManagerException(err)
        else:
            err = 'No working package manager for "{dep_t}" in {mgrs}'.format(dep_t=dep_t,
                                                                              mgrs=mgrs)
            raise exceptions.PackageManagerOperationalException(err)

    def _process_dependency(self, dep_t, dep_l):
        """Add dependencies into self.dependencies, possibly also adding system packages
        that contain non-distro package managers (e.g. if someone wants to install
        dependencines with pip and pip is not present, it will get installed through
        RPM on RPM based systems, etc.

        Skips dependencies that are supposed to be installed by system manager that
        is not native to this system.
        """
        if dep_t not in managers:
            err = 'No package manager for dependency type "{dep_t}"'.format(dep_t=dep_t)
            raise exceptions.NoPackageManagerException(err)
        # try to get list of distros where the dependency type is system type
        distro = settings.SYSTEM_DEPTYPES_SHORTCUTS.get(dep_t, None)
        if not distro: # non-distro dependency type
            sysdep_t = self.get_system_deptype_shortcut()
            # for now, just take the first manager that can install dep_t and install this manager
            self._process_dependency(sysdep_t,
                                     managers[dep_t][0].get_distro_dependencies(sysdep_t))
        elif utils.get_distro_name() not in distro: # distro dependency type, but for another distro
            return
        self.dependencies.setdefault(dep_t, [])
        self.dependencies[dep_t].extend(dep_l)

    def _ask_to_confirm(self, pac_man, *to_install):
        """ Return True if user wants to install packages, False otherwise """
        ret = DialogHelper.ask_for_package_list_confirm(
            prompt=pac_man.get_perm_prompt(to_install),
            package_list=to_install,
        )
        return False if ret is False else True

    def _install_dependencies(self):
        """Install missing dependencies"""
        for dep_t, dep_l in self.dependencies.items():
            if not dep_l:
                continue
            pkg_mgr = self.get_package_manager(dep_t)
            pkg_mgr.works()
            to_resolve = []
            for dep in dep_l:
                if not pkg_mgr.is_pkg_installed(dep):
                    to_resolve.append(dep)
            if not to_resolve:
                # nothing to install, let's move on
                continue
            to_install = pkg_mgr.resolve(*to_resolve)
            confirm = self._ask_to_confirm(pkg_mgr, *to_install)
            if not confirm:
                msg = 'List of packages denied by user, exiting.'
                raise exceptions.DependencyException(msg)

            type(self).install_lock = True
            # TODO: we should do this more systematically (send signal to cl/gui?)
            logger.info('Installing dependencies, sit back and relax ...',
                        extra={'event_type': 'dep_installation_start'})
            if current_run.UI == 'cli': # TODO: maybe let every manager to decide when to start
                event = threading.Event()
                t = FakeProgressThread(event)
                t.start()
            installed = pkg_mgr.install(*to_install)
            if current_run.UI == 'cli':
                event.set()
                t.join()
            type(self).install_lock = False

            log_extra = {'event_type': 'dep_installation_end'}
            if not installed:
                msg = 'Failed to install dependencies, exiting.'
                logger.error(msg, extra=log_extra)
                ex = exceptions.DependencyException(msg)
                ex.already_logged = True
                raise ex
            else:
                logger.info('Successfully installed dependencies!', extra=log_extra)

    def install(self, struct):
        """
        This is the only method that should be called from outside. Call it
        like:
        `DependencyInstaller(struct)` and it will install packages which are
        not present on system (it uses package managers specified by `struct`
        structure)
        """
        # the system dependencies should always go first
        self.dependencies.setdefault(self.get_system_deptype_shortcut(), [])
        for dep_dict in struct:
            for dep_t, dep_l in dep_dict.items():
                self._process_dependency(dep_t, dep_l)
        if self.dependencies:
            self._install_dependencies()

    def get_system_deptype_shortcut(self):
        distro = utils.get_distro_name()
        for k, v in settings.SYSTEM_DEPTYPES_SHORTCUTS.items():
            if distro in v:
                return k

        # just try rpm if unkown (not very nice?)
        return 'rpm'

class FakeProgressThread(threading.Thread):
    def __init__(self, finish_event):
        super(FakeProgressThread, self).__init__()
        self.finish_event = finish_event

    def run(self):
        wait_for = 1
        while not self.finish_event.isSet():
            print('.', end='')
            sys.stdout.flush()
            wait_for += 1
            self.finish_event.wait(math.log(wait_for))
        print()


def main():
    """ just for testing """
    import logging
    import sys
    from devassistant import logger as l
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(l.DevassistantClFormatter())
    console_handler.setLevel(logging.DEBUG)
    l.logger.addHandler(console_handler)

    di = DependencyInstaller()
    di.install([{'rpm': ['python-celery']}, {'pip': ['numpy', 'celery']}])

if __name__ == '__main__':
    main()
