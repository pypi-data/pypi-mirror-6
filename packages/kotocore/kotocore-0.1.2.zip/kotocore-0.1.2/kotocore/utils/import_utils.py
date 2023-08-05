import importlib

from kotocore.exceptions import IncorrectImportPath


def import_class(import_path):
    """
    Imports a class dynamically from a full import path.
    """
    if not '.' in import_path:
        raise IncorrectImportPath(
            "Invalid Python-style import path provided: {0}.".format(
                import_path
            )
        )

    path_bits = import_path.split('.')
    mod_path = '.'.join(path_bits[:-1])
    klass_name = path_bits[-1]

    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        raise IncorrectImportPath(
            "Could not import module '{0}'.".format(mod_path)
        )

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise IncorrectImportPath(
            "Imported module '{0}' but could not find class '{1}'.".format(
                mod_path,
                klass_name
            )
        )

    return klass
