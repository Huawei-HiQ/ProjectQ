#   Copyright 2017 ProjectQ-Framework (www.projectq.ch)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from pathlib import Path
import sys
import inspect
import pkgutil
from importlib import import_module

from ._basics import BasicEngine


def dynamic_import(name):
    imported_module = import_module('.' + name, package=__name__)

    for i in dir(imported_module):
        attribute = getattr(imported_module, i)

        if (inspect.isclass(attribute) and issubclass(attribute,
                                                      (BasicEngine, Exception))
                and not hasattr(sys.modules[__name__], i)):
            setattr(sys.modules[__name__], i, attribute)

        if i == 'all_defined_symbols':
            for symbol in attribute:
                if not hasattr(sys.modules[__name__], symbol.__name__):
                    setattr(sys.modules[__name__], symbol.__name__, symbol)


_priority_modules = [
    '_basics', '_cmdmodifier', '_basicmapper', '_linearmapper'
]
for name in _priority_modules:
    dynamic_import(name)

_failed_list = []
for (_, name, _) in pkgutil.iter_modules([Path(__file__).parent]):
    if name.endswith('test') or name in _priority_modules:
        continue
    try:
        dynamic_import(name)
    except ImportError:
        _failed_list.append(name)

for name in _failed_list:
    dynamic_import(name)

# Allow extending this namespace.
__path__ = pkgutil.extend_path(__path__, __name__)
