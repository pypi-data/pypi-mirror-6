'''
To compile another package that wants to link with the C code in pywcs:

[build_ext]
pre-hook.pywcs = pywcs.hooks.setup

[extension=drizzlepac.cdriz]
include_dirs = numpy pywcs
libraries = pywcs m

'''
import os

def setup(command_obj) :

    # warning if we somehow get called when not building a c extension
    command_name = command_obj.get_command_name()
    if command_name != 'build_ext':
        log.warn('%s is meant to be used with the build_ext command only; '
                 'it is not for use with the %s command.' %
                 (__name__, command_name))

    # get information from pywcs (ourselves)
    import pywcs
    pywcslib = pywcs.__path__[0]
    includes = [os.path.join(pywcslib, 'include'),
                         os.path.join(pywcslib, 'include', 'wcslib')]

    # each place where the include directory is named exactly "pywcs",
    # replace it with the include directories computed above
    for extension in command_obj.extensions:
        if 'pywcs' not in extension.include_dirs:
            continue
        idx = extension.include_dirs.index('pywcs')
        for inc in includes:
            extension.include_dirs.insert(idx, inc)
        extension.include_dirs.remove('pywcs')

