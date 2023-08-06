import os
import jsonschema
import imp
import importlib
import sys
from distutils.sysconfig import get_python_lib
from log import log
import libraries

class StateHandler:
    def __init__(self, library_dir):
        self.libraries = [library_dir, os.path.dirname(libraries.__file__)]

    def apply(self, library_name, inputhash, dry_run = False):
        """
        Changes the state of the system according to what the module
        specified does

        Keyword arguments:
            library_name -- the python module to load
            inputhash -- the list of dictionaries of config for the library
            dry_run -- whether or not to actually change the system
        """
        if library_name not in sys.modules:
            try:
                imp.acquire_lock()
                mod = imp.find_module(library_name, self.libraries)
                imp.load_module(library_name, *mod)
            except ImportError:
                log.exception("Couldn't find module %s in dirs %s", library_name, self.libraries)
                raise
            finally:
                if imp.lock_held():
                    imp.release_lock()

        library = importlib.import_module(library_name)
        schema = library.schema()

        for item in inputhash:
            jsonschema.validate(item, schema)

        failed = library.verify(inputhash)
 
        if not dry_run:
            library.apply(inputhashes=failed, log=log)
            failed = library.verify(inputhash)
            if len(failed) > 0:
                log.error("Failed for good on {}".format(failed))

        return failed
