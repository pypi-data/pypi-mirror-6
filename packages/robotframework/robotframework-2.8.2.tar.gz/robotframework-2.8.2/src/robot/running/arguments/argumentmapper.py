#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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


class ArgumentMapper(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def map(self, positional, named, variables=None, prune_trailing_defaults=False):
        template = KeywordCallTemplate(self._argspec, variables)
        template.fill_positional(positional)
        template.fill_named(named)
        if prune_trailing_defaults:
            template.prune_trailing_defaults()
        template.fill_defaults()
        return template.args, template.kwargs


class KeywordCallTemplate(object):

    def __init__(self, argspec, variables):
        defaults = argspec.defaults
        if variables:
            defaults = variables.replace_list(defaults)
        self._positional = argspec.positional
        self._kwargs_supported = bool(argspec.kwargs)
        self.args = [None] * argspec.minargs + [Default(d) for d in defaults]
        self.kwargs = {}

    def fill_positional(self, positional):
        self.args[:len(positional)] = positional

    def fill_named(self, named):
        for name, value in named.items():
            if name in self._positional:
                index = self._positional.index(name)
                self.args[index] = value
            elif self._kwargs_supported:
                self.kwargs[name] = value
            else:
                raise ValueError("Non-existing named argument '%s'" % name)

    def prune_trailing_defaults(self):
        while self.args and isinstance(self.args[-1], Default):
            self.args.pop()

    def fill_defaults(self):
        self.args = [arg if not isinstance(arg, Default) else arg.value
                     for arg in self.args]


class Default(object):

    def __init__(self, value):
        self.value = value
