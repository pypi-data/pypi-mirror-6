import pkg_resources
import os
import sys


class RequirementNotFoundError(Exception):
    pass


def collect_dependency_paths(package_name):
    """
    TODO docstrings
    """
    deps = []
    try:
        dist = pkg_resources.get_distribution(package_name)
    except (pkg_resources.DistributionNotFound, ValueError):
        message = "Distribution '{}' not found.".format(package_name)
        raise RequirementNotFoundError(message)

    if dist.has_metadata('top_level.txt'):
        for line in dist.get_metadata('top_level.txt').split():
            # do not consider subpackages (e.g. the form 'package/subpackage')
            if not os.path.split(line)[0]:
                pkg = os.path.join(dist.location, line)
                # handle single module packages
                if not os.path.isdir(pkg) and os.path.exists(pkg+'.py'):
                    pkg += '.py'
                deps.append(pkg)

    for req in dist.requires():
        deps.extend(collect_dependency_paths(req.project_name))

    return deps


def parse_requirements_file(req_file):
    """
    TODO docstrings
    """
    lines = []
    for line in req_file.readlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        lines.append(line)
    return lines


def make_simlinks(dest_dir, paths_list):
    """
    TODO docstrings
    """
    for path in paths_list:
        dest = os.path.join(dest_dir, os.path.split(path)[-1])
        if os.path.exists(dest):
            if os.path.islink(dest):
                os.remove(dest)
            else:
                sys.stderr.write('A file or dir named {} already exists, skipping...\n'.format(dest))
                continue
        os.symlink(path, dest)


def get_config_code(dependencies_root):
    """
    TODO docstrings
    """
    code = ("# code generated by Appengine Toolkit\n"
            "import sys\n"
            "import os\n"
            "sys.path.append(os.path.join(os.path.dirname(__file__), '{}'))\n"
            "# end generated code\n".format(dependencies_root))

    return code
