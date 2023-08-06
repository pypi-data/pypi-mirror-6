# Blackskirt - Relative weekday/date utilities useful for finding
# public holidays
# Copyright (C) 2014  James Nah <sangho.nah@gmail.com>
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

import blackskirt

setup(name="Blackskirt",
      version=blackskirt.__version__,
      description=("Relative weekday/date utilities "
                   "useful for finding public holidays"),
      long_description=open("README.rst").read(),
      author="James Nah",
      author_email="sangho.nah@gmail.com",
      url="https://github.com/microamp/blackskirt",
      packages=find_packages(),
      package_data={"": ["README.rst", "LICENSE", "LGPL"]},
      include_package_data=True,
      license="GNU Lesser General Public License v3 or later (LGPLv3+)",
      zip_safe=False,
      classifiers=("Development Status :: 2 - Pre-Alpha",
                   "Intended Audience :: Developers",
                   ("License :: OSI Approved :: "
                    "GNU Lesser General Public License v3 or later (LGPLv3+)"),
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Topic :: Software Development :: Libraries",))
