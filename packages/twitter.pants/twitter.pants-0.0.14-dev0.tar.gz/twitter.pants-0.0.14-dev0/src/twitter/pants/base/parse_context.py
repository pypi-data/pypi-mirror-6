# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

import collections
import copy
import os
import sys

from contextlib import contextmanager

from twitter.common.lang import Compatibility

from twitter.pants import get_buildroot
from twitter.pants.base import BuildFile, Config


class ParseContext(object):
  """Defines the context of a parseable BUILD file target and provides a mechanism for targets to
  discover their context when invoked via eval.
  """

  class ContextError(Exception):
    """Indicates an action that requires a BUILD file parse context was attempted outside any."""

  _active = collections.deque([])
  _parsed = set()

  @classmethod
  def locate(cls):
    """Attempts to find the current root directory and buildfile.

    If there is an active parse context (see do_in_context), then it is returned.
    """
    if not ParseContext._active:
      raise cls.ContextError('No parse context active.')
    return ParseContext._active[-1]

  @staticmethod
  @contextmanager
  def temp(basedir=None):
    """Activates a temporary parse context in the given basedir relative to the build root or else
    in the build root dir itself if no basedir is specified.
    """
    context = ParseContext(BuildFile(get_buildroot(), basedir or 'BUILD.temp', must_exist=False))
    with ParseContext.activate(context):
      yield

  @classmethod
  @contextmanager
  def activate(cls, ctx):
    """Activates the given ParseContext."""
    if hasattr(ctx, '_on_context_exit'):
      raise cls.ContextError('Context actions registered outside this parse context arg active')

    try:
      ParseContext._active.append(ctx)
      ctx._on_context_exit = []
      yield
    finally:
      for func, args, kwargs in ctx._on_context_exit:
        func(*args, **kwargs)
      del ctx._on_context_exit
      ParseContext._active.pop()

  def __init__(self, buildfile):
    self.buildfile = buildfile
    self._active_buildfile = buildfile
    self._parsed = False

  @staticmethod
  def default_globals(config=None):
    """
    Has twitter.pants.*, but not file-specfic things like __file__
    If you want to add new imports to be available to all BUILD files, add a section to the config similar to:
    [parse]
    headers: ['from test import get_jar',]

    You may also need to add new roots to the sys.path. see _run in pants_exe.py
    """
    pants_context = {}
    ast1 = compile("from twitter.pants import *", "<string>", "exec")
    ast2 = compile("from twitter.common.quantity import Amount, Time", "<string>", "exec")
    Compatibility.exec_function(ast1, pants_context)
    Compatibility.exec_function(ast2, pants_context)

    # TODO: This can be replaced once extensions are enabled with https://github.com/pantsbuild/pants/issues/5
    if config:
      headers = config.getlist('parse', 'headers', default=[])
      for exec_file in headers:
        ast1 = compile(exec_file, "<string>", "exec")
        Compatibility.exec_function(ast1, pants_context)

    return pants_context

  def parse(self, **globalargs):
    """The entry point to parsing of a BUILD file.

    Changes the working directory to the BUILD file directory and then evaluates the BUILD file
    with the ROOT_DIR and __file__ globals set in addition to any globals specified as kwargs.  As
    target methods are parsed they can examine the stack to find these globals and thus locate
    themselves for the purposes of finding files.

    See locate().
    """
    if self.buildfile not in ParseContext._parsed:
      buildfile_family = tuple(self.buildfile.family())

      pants_context = self.default_globals(Config.load())

      with ParseContext.activate(self):
        start = os.path.abspath(os.curdir)
        try:
          os.chdir(self.buildfile.parent_path)
          for buildfile in buildfile_family:
            self._active_buildfile = buildfile
            # We may have traversed a sibling already, guard against re-parsing it.
            if buildfile not in ParseContext._parsed:
              ParseContext._parsed.add(buildfile)

              eval_globals = copy.copy(pants_context)
              eval_globals.update({
                  'ROOT_DIR': buildfile.root_dir,
                  '__file__': buildfile.full_path,
              })
              eval_globals.update(globalargs)
              Compatibility.exec_function(buildfile.code(), eval_globals)
        finally:
          os.chdir(start)

  def on_context_exit(self, func, *args, **kwargs):
    """ Registers a command to invoke just before this parse context is exited.

    It is an error to attempt to register an on_context_exit action outside an active parse
    context.
    """
    if not hasattr(self, '_on_context_exit'):
      raise self.ContextError('Can only register context exit actions when a parse context '
                              'is active')

    if not callable(func):
      raise TypeError('func must be a callable object')

    self._on_context_exit.append((func, args, kwargs))

  def do_in_context(self, work):
    """Executes the callable work in this parse context."""
    if not callable(work):
      raise TypeError('work must be a callable object')

    with ParseContext.activate(self):
      return work()

  def __repr__(self):
    return '%s(%s)' % (type(self).__name__, self.buildfile)

  @property
  def current_buildfile(self):
    """ This property return the current build file being parsed from all BUILD files co-located
    with this BUILD file within the family.
    """
    return self._active_buildfile
