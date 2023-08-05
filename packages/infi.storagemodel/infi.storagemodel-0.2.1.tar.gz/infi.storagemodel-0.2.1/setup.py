
SETUP_INFO = dict(
    name = 'infi.storagemodel',
    version = '0.2.1',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.storagemodel',
    license = 'PSF',
    description = """A high-level library for traversing the OS storage model.""",
    long_description = """A high-level cross-platform abstraction of the OS storage stack (LUNs, disks, volumes, etc).""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.pyutils>=1.0.3', 'infi.wioctl>=0.1.3', 'infi.multipathtools>=0.1.18', 'infi.wmpio>=0.1.16', 'infi.diskmanagement>=0.3', 'infi.exceptools>=0.2.2', 'Brownie>=0.5.1', 'infi.mountoolinux>=0.1.9', 'infi.parted>=0.2', 'infi.cwrap>=0.2.4', 'daemon>=1.0', 'infi.dtypes.wwn>=0.0.2', 'infi.dtypes.hctl>=0.0.6', 'infi.sgutils>=0.1.1', 'infi.devicemanager>=0.2.5', 'infi.hbaapi>0.1.21', 'infi.traceback>=0.3.5', 'infi.instruct>=0.6.16', 'distribute>=0.7.3', 'infi.asi>=0.3.17'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['devlist = infi.storagemodel.examples:devlist', 'rescan_scsi_bus = infi.storagemodel.linux.rescan_scsi_bus:console_script'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

