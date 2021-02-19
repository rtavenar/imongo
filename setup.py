#!/usr/bin/env python
import json
import os
import sys
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

if sys.version_info < (3, 6):
    sys.exit('IMongo supports Python 3.6+ only')

class CommandMixin(object):
    user_options = [
        ('nokernelinstall', None,
         'if this flag is passed the kernel is not added to the list of ' +
         'jupyter kernels at the end of install')
    ]

    def initialize_options(self):
        super().initialize_options()
        self.nokernelinstall = None

    def finalize_options(self):
        super().finalize_options()

    def _post_install(self):
        print("install attributes: {}".format(install.__dict__))
        if self.nokernelinstall:
            return
        if not hasattr(self, "user"):
            self.user = False
        if not hasattr(self, "prefix"):
            self.prefix = None

        print('Installing Jupyter kernelspec')
        from jupyter_client.kernelspec import KernelSpecManager
        from IPython.utils.tempdir import TemporaryDirectory
        kernel_json = {
            "argv": ["python", "-m", "imongo", "-f", "{connection_file}"],
            "codemirror_mode": "shell",
            "display_name": "IMongo"
        }
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            ksm = KernelSpecManager()
            ksm.install_kernel_spec(td, 'imongo', replace=True,
                                    user=self.user, prefix=self.prefix)


class Installer(CommandMixin, install):
    user_options = install.user_options + CommandMixin.user_options
    def run(self):
        # Regular install
        install.run(self)

        # Post install
        self._post_install()

class DevelopCommand(CommandMixin, develop):
    user_options = develop.user_options + CommandMixin.user_options
    def run(self):
        # Regular install
        develop.run(self)

        # Post install
        self._post_install()


class EggInfoCommand(CommandMixin, egg_info):
    user_options = egg_info.user_options + CommandMixin.user_options
    def run(self):
        # Regular install
        egg_info.run(self)

        # Post install
        self._post_install()



with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name='imongo-kernel',
      version='0.1.0',
      description='A MongoDB kernel for Jupyter',
      long_description=long_description,
      author='Gustavo Bezerra',
      author_email='gusutabopb@gmail.com',
      url='https://github.com/gusutabopb/imongo',
      packages=['imongo'],
      cmdclass={
        'install': Installer,
        'develop': DevelopCommand,
        'egg_info': EggInfoCommand
      },
      license='MIT',
      include_package_data=True,
      install_requires=['jupyter>=1.0.0',
                        'ipykernel',
                        'pexpect>=4.2.1',
                        'pyyaml'],
      python_requires='>=3.6',
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Science/Research',
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Shells',
      ])
