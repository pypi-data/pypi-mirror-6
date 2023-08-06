import hashlib
import os
import subprocess

from . import util

def get_dpkg_field(path, field):
    return _dpkg_deb(['--field', path, field], unicode=True).strip()

def get_dpkg_info(path):
    return _dpkg_deb(['--field', path])

def get_apt_package_info(path, relative_pool_root):
    return (
        get_dpkg_info(path) +
        _get_filename_line(path, relative_pool_root) +
        _get_additional_apt_info(path)
    )

def get_pool_path(package_path, pool_root):
    filename = os.path.basename(package_path)
    package_name = get_dpkg_field(package_path, 'Package')

    prefix = (
        package_name[:4]
        if package_name.startswith('lib')
        else package_name[0]
    )

    return os.path.join(
        pool_root,
        prefix,
        package_name,
        filename,
    )

def _dpkg_deb(command, unicode=False):
    return subprocess.check_output(
        ['dpkg-deb'] + command,
        universal_newlines=unicode,
    )

def _get_filename_line(path, relative_pool_root):
    line = 'Filename: %s\n' % get_pool_path(path, relative_pool_root)
    return line.encode('ascii')

def _get_additional_apt_info(path):
    hashes = [
        ('MD5sum', hashlib.md5()),
        ('SHA1', hashlib.sha1()),
        ('SHA256', hashlib.sha256()),
    ]

    size = 0
    for chunk in util.read_in_chunks(path):
        for _, hasher in hashes:
            hasher.update(chunk)

        size += len(chunk)

    digests = ''.join(
        '%s: %s\n' % (algorithm, hasher.hexdigest())
        for algorithm, hasher in hashes
    )
    additional_apt_info = digests + 'Size: %d\n' % size

    return additional_apt_info.encode('ascii')
