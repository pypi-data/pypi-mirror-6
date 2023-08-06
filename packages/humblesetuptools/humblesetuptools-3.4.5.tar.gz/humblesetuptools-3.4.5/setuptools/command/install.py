import setuptools
import inspect
import glob
import warnings
import platform
from distutils.command.install import install as _install
from distutils.errors import DistutilsArgError

class install(_install):
    """Use easy_install to install the package, w/dependencies"""

    user_options = _install.user_options + [
        ('old-and-unmanageable', None, "No-op, exists for backwards compat"),
        ('single-version-externally-managed', None,
            "No-op, exists for backwards compat"),
    ]
    boolean_options = _install.boolean_options + [
        'old-and-unmanageable', 'single-version-externally-managed',
    ]
    new_commands = [
        ('install_egg_info', lambda self: True),
        ('install_scripts', lambda self: True),
    ]
    _nc = dict(new_commands)

    def initialize_options(self):
        _install.initialize_options(self)
        self.old_and_unmanageable = None
        self.single_version_externally_managed = None

    def finalize_options(self):
        _install.finalize_options(self)
        self.old_and_unmanageable = True
        self.single_version_externally_managed = True

    # handle_extra_path is no longer overridden

    # run is no longer overridden

# XXX Python 3.1 doesn't see _nc if this is inside the class
install.sub_commands = [
        cmd for cmd in _install.sub_commands if cmd[0] not in install._nc
    ] + install.new_commands
