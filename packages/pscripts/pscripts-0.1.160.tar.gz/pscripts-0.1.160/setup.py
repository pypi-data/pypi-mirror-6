from setuptools import setup
from setuptools.command.install  import  install  as  _install
from setuptools import setup
import os, pdb, shutil
version='0.1.160'
name='pscripts'
scripts = [
    'scripts/python-deployment',
    'scripts/hdmi_brightness',
    'scripts/update_external_ip',
    'scripts/cp_exe_2_chroot_jail',
    'scripts/laptop_battery',
]
classifiers = [ 'Programming Language :: Python :: 3.3',
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Natural Language :: English',
                'Operating System :: POSIX :: Linux',
                'Topic :: System :: Systems Administration',
                'Topic :: Utilities',
            ]
install_requires=[
    'setuptools',
    'SimpleDaemon >= 1.3.0',
    'PyYAML >= 3.10',
    'pidfile >= 0.1.0',
    'requests >= 2.0.0',
]

# this nonesense is so that we have a way to not over-write the 
# config files of previous installs.  If they are present it
# just adds them to that directory with a *.generic suffix.
class install(_install):
    config_files=[('/etc/external_ip_updater/', 
                 ['urls.yaml','config.conf']),
                ('/usr/lib/systemd/system/',
                 ['update_external_ip.service']),
                ('/etc/pscripts/',
                 ['pscripts.yaml']),]

    def run(self):
        _install.run(self)
        for file_tuple in self.config_files:
            target_dir = file_tuple[0]
            files_to_copy = file_tuple[1]
            for curr_file in files_to_copy:
                self.copy_config_file(target_dir, curr_file)

    # helper
    def copy_config_file(self, target_dir, conf_file):
        src_file = "config/" + conf_file
        target_file = target_dir + conf_file
        if not os.path.exists(target_dir): # make parent folders
            os.makedirs(target_dir)
        if os.path.isfile( target_dir + conf_file ): # save file with template extension
            shutil.copy(src_file, target_file + ".template" )
        else: # just copy over file
            shutil.copy(src_file, target_file )

setup(
    name = name,
    version = version,
    packages = [name],
    description = 'Automation Scripts for Linux',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='www.google.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='Automates some python deployment steps',
    classifiers=classifiers,
    scripts = scripts,
    install_requires=install_requires,
    cmdclass={'install': install},
)
