# ==================================================================================================
# Copyright 2012 Twitter, Inc.
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

__author__ = 'Brian Larson'

import os

from twitter.common.collections import OrderedSet
from twitter.common.dirutil import safe_mkdir

from twitter.pants import is_jvm
from twitter.pants.targets import JavaLibrary, JavaAntlrLibrary
from twitter.pants.tasks import TaskError
from twitter.pants.tasks.code_gen import CodeGen
from twitter.pants.tasks.nailgun_task import NailgunTask


class AntlrGen(CodeGen, NailgunTask):

  # Maps the compiler attribute of a target to the config key in pants.ini
  _CONFIG_SECTION_BY_COMPILER = {
    'antlr3': 'antlr-gen',
    'antlr4': 'antlr4-gen',
  }

  def __init__(self, context):
    CodeGen.__init__(self, context)
    NailgunTask.__init__(self, context)
    self._classpath_by_profile = {}

  def is_gentarget(self, target):
    return isinstance(target, JavaAntlrLibrary)

  def is_forced(self, lang):
    return True

  def genlangs(self):
    return dict(java=is_jvm)

  def prepare_gen(self, targets):
    for target in targets:
      antlr_profile = self._antlr_profile(target)
      if antlr_profile not in self._classpath_by_profile:
        antlr_classpath = self.profile_classpath(antlr_profile)
        self._classpath_by_profile[antlr_profile] = antlr_classpath

  def genlang(self, lang, targets):
    if lang != 'java':
      raise TaskError('Unrecognized antlr gen lang: %s' % lang)

    # TODO: Instead of running the compiler for each target, collect the targets
    # by type and invoke it twice, once for antlr3 and once for antlr4.

    for target in targets:
      java_out = self._java_out(target)
      safe_mkdir(java_out)

      antlr_profile = self._antlr_profile(target)
      antlr_classpath = self._classpath_by_profile[antlr_profile]
      args = ["-o", java_out]

      if target.compiler == 'antlr3':
        antlr_main = 'org.antlr.Tool'
      elif target.compiler == 'antlr4':
        args.append("-visitor")  # Generate Parse Tree Visitor As Well
        antlr_main = 'org.antlr.v4.Tool'
      else:
        raise TaskError("Unknown ANTLR compiler: {}".format(target.compiler))

      sources = self._calculate_sources([target])
      args.extend(sources)
      result = self.runjava(antlr_classpath, antlr_main, args=args)
      if result != 0:
        raise TaskError('java %s ... exited non-zero (%i)' % (antlr_main, result))

  def _calculate_sources(self, targets):
    sources = set()

    def collect_sources(target):
      if self.is_gentarget(target):
        sources.update(os.path.join(target.target_base, source) for source in target.sources)
    for target in targets:
      target.walk(collect_sources)
    return sources

  def createtarget(self, lang, gentarget, dependees):
    if lang != 'java':
      raise TaskError('Unrecognized antlr gen lang: %s' % lang)
    return self._create_java_target(gentarget, dependees)

  def _create_java_target(self, target, dependees):
    antlr_files_suffix = ["Lexer.java", "Parser.java"]
    if (target.compiler == 'antlr4'):
      antlr_files_suffix = ["BaseListener.java", "BaseVisitor.java",
                            "Listener.java", "Visitor.java"] + antlr_files_suffix

    generated_sources = []
    for source in target.sources:
      # Antlr enforces that generated sources are relative to the base filename, and that
      # each grammar filename must match the resulting grammar Lexer and Parser classes.
      source_base, source_ext = os.path.splitext(source)
      for suffix in antlr_files_suffix:
        generated_sources.append(source_base + suffix)

    deps = self._resolve_java_deps(target)

    tgt = self.context.add_new_target(os.path.join(self._java_out(target), target.target_base),
                                      JavaLibrary,
                                      name=target.id,
                                      provides=target.provides,
                                      sources=generated_sources,
                                      dependencies=deps)
    tgt.id = target.id
    tgt.is_codegen = True
    for dependee in dependees:
      dependee.update_dependencies([tgt])
    return tgt

  def _resolve_java_deps(self, target):
    key = self._CONFIG_SECTION_BY_COMPILER[target.compiler]

    deps = OrderedSet()
    for dep in self.context.config.getlist(key, 'javadeps'):
        deps.update(self.context.resolve(dep))
    return deps

  def _antlr_profile(self, target):
    key = self._CONFIG_SECTION_BY_COMPILER[target.compiler]
    return self.context.config.get(key, 'antlr_profile')

  def _java_out(self, target):
    key = self._CONFIG_SECTION_BY_COMPILER[target.compiler]
    return os.path.join(self.context.config.get(key, 'workdir'), 'gen-java')
