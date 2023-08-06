import sys
import os
import setuptools
import imp


def get_setup_data(path):
    """get the arguments of setup() call inside a setup.py by executing it

    The only way to get data out of a setup.py is by executing it.  The setuptools
    setup() function is mocked to extract the desired information

    This is potentially dangerous and error prone.

    :param path: path to the setup.py file
    :type path: str
    :rtype: dict
    """
    data = {}

    # save old state
    old_setup = setuptools.setup
    old_pwd = os.curdir
    old_modules = sys.modules.keys()
    try:
        import distutils.core
        old_distutils = distutils.core.setup
    except Exception:
        old_distutils = None

    # mock setuptools and distutils
    def s(**kwargs):
        data.update(kwargs)

    setuptools.setup = s
    if old_distutils:
        distutils.core.setup = s

    # import setup.py
    os.chdir(os.path.dirname(path))
    imp.load_source('fake-load-setup-py', path)

    # cleanup
    for module in sys.modules.keys():
        if module not in old_modules:
            del sys.modules[module]

    setuptools.setup = old_setup
    if old_distutils:
        distutils.core.setup = old_distutils
    os.chdir(old_pwd)
    return data
