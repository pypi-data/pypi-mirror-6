"""
This file is part of SubDownloaderLite.

    SubDownloaderLite is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    SubDownloaderLite is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

VERSION = (0, 1, 0, 'alpha', 0)


def get_version(*args, **kwargs):
    from subdownloader.utils.version import get_version
    return get_version(*args, **kwargs)
