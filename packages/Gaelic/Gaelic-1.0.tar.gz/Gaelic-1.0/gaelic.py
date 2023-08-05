import pkg_resources
import shutil
import os
import argparse
import glob
import subprocess
import re


def read_requirements(reqfile):
    with open(reqfile, 'r') as file:
        data = file.read()
        requirements = list(pkg_resources.parse_requirements(data))
    return requirements


def clean_destination(target):
    if not os.path.exists(target):
        os.mkdir(target)
    files = glob.glob(os.path.join(target, "*"))
    for file in files:
        shutil.rmtree(file, True)


def clean_eggs(target):
    files = glob.glob(os.path.join(target, "*.egg-info"))
    for file in files:
        shutil.rmtree(file, True)
    files = glob.glob(os.path.join(target, "*.dist-info"))
    for file in files:
        shutil.rmtree(file, True)


def pip_install(target, package):
    subprocess.check_call(["pip", "install", "--target", target, package])


def install_packages(packages, destination):
    """
    Installs all of the listed packages
    """
    for pkg in packages:
        pip_install(destination, str(pkg))


def install_hook(destination):
    rx = re.compile(r'\# --- START GAELIC IMPORTER ---(.+)\# --- END GAELIC IMPORTER ---\n', re.DOTALL)
    output = ''
    if os.path.exists('appengine_config.py'):
        with open('appengine_config.py') as f:
            output = f.read()

    output = rx.sub('', output)

    hook = """
# --- START GAELIC IMPORTER ---

def gaelic_fix_path(path):
    import sys, os
    base = os.path.dirname(__file__)
    lib = os.path.join(base, path)
    if not lib in sys.path:
        sys.path.append(lib)


gaelic_fix_path('%s')

# --- END GAELIC IMPORTER ---\n
""" % (destination)

    output = hook + output.strip()

    with open('appengine_config.py', 'w') as f:
        f.write(output)


def main():
    parser = argparse.ArgumentParser(description='Gaelic (App Engine Link) installs packages for App Engine projects.')
    parser.add_argument('-r', '--requirements', help="pip requirements file", default="requirements.txt")
    parser.add_argument('-t', '--target', help="Directory to install packages (./lib)", default="lib")
    args = parser.parse_args()

    clean_destination(args.target)
    requirements = read_requirements(args.requirements)
    install_packages(requirements, args.target)
    print 'Cleaning eggs'
    clean_eggs(args.target)
    print 'Installing importer hook'
    install_hook(args.target)
    print 'Done!'


if __name__ == "__main__":
    main()
