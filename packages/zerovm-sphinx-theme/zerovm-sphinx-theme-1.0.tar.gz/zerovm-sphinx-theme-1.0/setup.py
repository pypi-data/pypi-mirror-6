#  Copyright 2014 Rackspace, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from distutils.core import setup

setup(name='zerovm-sphinx-theme',
      version='1.0',
      description='ZeroVM theme for Sphinx',
      long_description=open('README.rst').read(),
      author='Martin Geisler',
      author_email='martin@geisler.net',
      url='https://github.com/zerovm/sphinx-theme',
      packages=['zerovm_sphinx_theme'],
      package_data={'zerovm_sphinx_theme': ['zerovm/theme.conf',
                                            'zerovm/static/*.css',
                                            'zerovm/static/*.css_t']}
)
