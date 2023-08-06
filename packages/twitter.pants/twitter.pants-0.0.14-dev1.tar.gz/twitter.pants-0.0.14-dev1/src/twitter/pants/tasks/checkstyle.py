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

import os

from twitter.common.dirutil import safe_open
from twitter.pants import has_sources, is_codegen
from twitter.pants.process.xargs import Xargs
from twitter.pants.tasks import TaskError
from twitter.pants.tasks.nailgun_task import NailgunTask


CHECKSTYLE_MAIN = 'com.puppycrawl.tools.checkstyle.Main'


class Checkstyle(NailgunTask):
  @staticmethod
  def _is_checked(target):
    return has_sources(target, '.java') and not is_codegen(target)

  @classmethod
  def setup_parser(cls, option_group, args, mkflag):
    NailgunTask.setup_parser(option_group, args, mkflag)

    option_group.add_option(mkflag("skip"), mkflag("skip", negate=True),
                            dest="checkstyle_skip", default=False,
                            action="callback", callback=mkflag.set_bool,
                            help="[%default] Skip checkstyle.")

  def __init__(self, context):
    super(Checkstyle, self).__init__(context)

    self._profile = context.config.get('checkstyle', 'profile')
    self._configuration_file = context.config.get('checkstyle', 'configuration')
    self._work_dir = context.config.get('checkstyle', 'workdir')
    self._properties = context.config.getdict('checkstyle', 'properties')
    self._confs = context.config.getlist('checkstyle', 'confs')

  def execute(self, targets):
    if not self.context.options.checkstyle_skip:
      checkstyle_classpath = self.profile_classpath(self._profile)
      with self.changed(filter(Checkstyle._is_checked, targets)) as changed_targets:
        sources = self.calculate_sources(changed_targets)
        if sources:
          result = self.checkstyle(checkstyle_classpath, sources)
          if result != 0:
            raise TaskError('java %s ... exited non-zero (%i)' % (CHECKSTYLE_MAIN, result))

  def calculate_sources(self, targets):
    sources = set()
    for target in targets:
      sources.update([os.path.join(target.target_base, source)
                      for source in target.sources if source.endswith('.java')])
    return sources

  def checkstyle(self, checkstyle_classpath, sources):
    with self.context.state('classpath', []) as cp:
      checkstyle_classpath.extend(jar for conf, jar in cp if conf in self._confs)

    opts = [
      '-c', self._configuration_file,
      '-f', 'plain'
    ]

    if self._properties:
      properties_file = os.path.join(self._work_dir, 'checkstyle.properties')
      with safe_open(properties_file, 'w') as pf:
        for k, v in self._properties.items():
          pf.write('%s=%s\n' % (k, v))
      opts.extend(['-p', properties_file])

    # We've hit known cases of checkstyle command lines being too long for the system so we guard
    # with Xargs since checkstyle does not accept, for example, @argfile style arguments.
    def call(args):
      return self.runjava(checkstyle_classpath, CHECKSTYLE_MAIN, args=opts + args)
    checks = Xargs(call)

    return checks.execute(sources)
