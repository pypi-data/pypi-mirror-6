import collections
import hashlib
import io
import os
import posixpath
import shutil
import subprocess

from . import dpkg
from . import util

Package = collections.namedtuple(
    'Package',
    'name version architecture path'
)

def generate_repository(origin, input_path, output_path, key_id=None):
    for dist_name, components in _walk_dists_tree(input_path):
        dist_root = os.path.join(output_path, 'dists', dist_name)
        relative_pool_root = os.path.join('pool', dist_name)
        pool_root = os.path.join(output_path, relative_pool_root)

        os.makedirs(dist_root, exist_ok=True)
        os.makedirs(pool_root, exist_ok=True)

        _generate_dist(
            origin,
            dist_name,
            dist_root,
            pool_root,
            relative_pool_root,
            components,
            key_id,
        )

def _walk_dists_tree(root_path):
    for filename in sorted(os.listdir(root_path)):
        path = os.path.join(root_path, filename)

        if os.path.isdir(path):
            yield filename, list(_walk_components_tree(path))

def _walk_components_tree(root_path):
    for filename in sorted(os.listdir(root_path)):
        path = os.path.join(root_path, filename)

        if os.path.isdir(path):
            yield filename, list(_walk_packages_tree(path))

def _walk_packages_tree(root_path):
    for filename in sorted(os.listdir(root_path)):
        path = os.path.join(root_path, filename)

        if os.path.splitext(path)[1] == '.deb':
            yield _read_package_metadata(path)

def _read_package_metadata(path):
    return Package(
        dpkg.get_dpkg_field(path, 'Package'),
        dpkg.get_dpkg_field(path, 'Version'),
        dpkg.get_dpkg_field(path, 'Architecture'),
        path,
    )

def _generate_dist(origin, name, dist_root, pool_root, relative_pool_root,
                   components, key_id):
    architectures = set()
    index_files = []

    for component_name, packages in components:
        component_dist_root = os.path.join(dist_root, component_name)
        component_pool_root = os.path.join(pool_root, component_name)
        relative_component_pool_root = os.path.join(
            relative_pool_root,
            component_name
        )

        os.makedirs(component_pool_root, exist_ok=True)

        component_index_files, component_architectures = _generate_component(
            origin,
            name,
            component_name,
            component_dist_root,
            component_pool_root,
            relative_component_pool_root,
            packages,
        )

        index_files.extend(component_index_files)
        architectures.update(component_architectures)

    _write_dist_release_files(
        origin,
        name,
        dist_root,
        [component_name for component_name, packages in components],
        architectures,
        index_files,
        key_id,
    )

def _generate_component(origin, dist_name, name, dist_root, pool_root,
                        relative_pool_root, packages):
    architectures = {package.architecture for package in packages}
    index_files = []

    if 'amd64' in architectures:
        # At least on Ubuntu Precise (12.04), apt-get insists on seeking out
        # binary-i386/packages on amd64 systems, even if the top-level Release
        # file doesn't list the i386 architecture.
        architectures.add('i386')

    for architecture in architectures:
        relative_arch_dist_root = os.path.join(
            name,
            'binary-%s' % architecture,
        )
        arch_dist_root = os.path.join(dist_root, 'binary-%s' % architecture)
        os.makedirs(arch_dist_root, exist_ok=True)

        _write_arch_release_file(
            arch_dist_root,
            origin,
            dist_name,
            name,
            architecture,
        )
        index_files.append(os.path.join(relative_arch_dist_root, 'Release'))

        arch_packages = [
            package
            for package in packages
            if package.architecture in [architecture, 'all']
        ]

        index_files.extend(
            _write_packages_files(
                arch_dist_root,
                relative_arch_dist_root,
                relative_pool_root,
                arch_packages,
            )
        )

    for package in packages:
        pool_path = dpkg.get_pool_path(package.path, pool_root)
        os.makedirs(os.path.dirname(pool_path), exist_ok=True)
        shutil.copy2(package.path, pool_path)

    return index_files, architectures

def _write_arch_release_file(arch_dist_root, origin, dist_name, component_name,
                             architecture):
    release_path = os.path.join(arch_dist_root, 'Release')
    release_contents = ''.join([
        'Archive: %s\n' % dist_name,
        'Component: %s\n' % component_name,
        'Origin: %s\n' % origin,
        'Label: %s\n' % origin,
        'Architecture: %s\n' % architecture,
    ])

    with open(release_path, 'wb') as f:
        f.write(release_contents.encode('ascii'))

def _write_packages_files(arch_dist_root, relative_arch_dist_root,
                          relative_pool_root, arch_packages):
    output = []

    packages_path = os.path.join(arch_dist_root, 'Packages')
    with open(packages_path, 'wb') as f:
        for package in arch_packages:
            f.write(dpkg.get_apt_package_info(package.path, relative_pool_root))
            f.write(b'\n')
    output.append(posixpath.join(relative_arch_dist_root, 'Packages'))

    subprocess.check_call(
        'gzip --best < Packages > Packages.gz',
        shell=True,
        cwd=arch_dist_root,
    )
    output.append(posixpath.join(relative_arch_dist_root, 'Packages.gz'))

    if util.has_program('xz'):
        subprocess.check_call(
            'xz -9 < Packages > Packages.xz',
            shell=True,
            cwd=arch_dist_root,
        )
        output.append(posixpath.join(relative_arch_dist_root, 'Packages.xz'))

    return output

def _write_dist_release_files(origin, dist_name, dist_root, component_names,
                              architectures, index_files, key_id):

    hash_implementations = [
        ('MD5Sum', hashlib.md5),
        ('SHA1', hashlib.sha1),
        ('SHA256', hashlib.sha256),
    ]

    with open(os.path.join(dist_root, 'Release'), 'wt', encoding='ascii') as f:
        f.write('Origin: %s\n' % origin)
        f.write('Label: %s\n' % origin)
        f.write('Suite: %s\n' % dist_name)
        f.write('Codename: %s\n' % dist_name)
        f.write('Components: %s\n' % ' '.join(sorted(component_names)))
        f.write('Architectures: %s\n' % ' '.join(sorted(architectures)))

        digests = []
        for index_file in index_files:
            path = os.path.join(dist_root, index_file)

            hashers = {name: impl() for name, impl in hash_implementations}

            size = 0
            for chunk in util.read_in_chunks(path):
                for hasher in hashers.values():
                    hasher.update(chunk)

                size += len(chunk)

            digests.append((
                index_file,
                size,
                {name: hasher.hexdigest() for name, hasher in hashers.items()},
            ))

        for algorithm, _ in hash_implementations:
            f.write('%s:\n' % algorithm)

            for index_file, size, file_digests in digests:
                f.write(' %s %d %s\n' % (
                    file_digests[algorithm],
                    size,
                    index_file,
                ))

    gpg = 'gpg -u %s' % key_id if key_id else 'gpg'

    subprocess.check_call(
        '%s --sign < Release > Release.gpg' % gpg,
        shell=True,
        cwd=dist_root,
    )

    subprocess.check_call(
        '%s --clearsign < Release > InRelease' % gpg,
        shell=True,
        cwd=dist_root,
    )
