# ==================================================================================================
# Copyright 2013 Twitter, Inc.
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
import shutil

from twitter.pants.ivy import profile_classpath
from twitter.pants.java import runjava

from .jvm_task import JvmTask

from . import Task, TaskError


class BenchmarkRun(JvmTask):
  @classmethod
  def setup_parser(cls, option_group, args, mkflag):
    option_group.add_option(mkflag("target"), dest="target_class", action="append",
                            help="Name of the benchmark class.")

    option_group.add_option(mkflag("memory"), mkflag("memory", negate=True),
                            dest="memory_profiling", default=False,
                            action="callback", callback=mkflag.set_bool,
                            help="[%default] Enable memory profiling.")

    option_group.add_option(mkflag("debug"), mkflag("debug", negate=True),
                            dest="debug", default=False,
                            action="callback", callback=mkflag.set_bool,
                            help="[%default] Enable caliper debug mode.")

    option_group.add_option(mkflag("caliper-args"), dest="extra_caliper_args", default=[],
                            action="append",
                            help="Allows the user to pass additional command line options to "
                                 "caliper. Can be used multiple times and arguments will be "
                                 "concatenated. Example use: --bench-caliper-args='-Dsize=10,20 "
                                 "-Dcomplex=true,false' --bench-caliper-args=-Dmem=1,2,3")

  def __init__(self, context):
    Task.__init__(self, context)
    self.profile = context.config.get('benchmark-run', 'profile',
                                      default="benchmark-caliper-0.5")
    self.confs = context.config.getlist('benchmark-run', 'confs')
    self.jvm_args = context.config.getlist('benchmark-run', 'jvm_args',
                                            default=['-Xmx1g', '-XX:MaxPermSize=256m'])
    self.agent_profile = context.config.get('benchmark-run', 'agent_profile',
                                            default="benchmark-java-allocation-instrumenter-2.1")
    # TODO(Steve Gury):
    # Find all the target classes from the Benchmark target itself
    # https://jira.twitter.biz/browse/AWESOME-1938
    self.caliper_args = context.options.target_class

    if context.options.memory_profiling:
      self.caliper_args += ['--measureMemory']
      # For rewriting JDK classes to work, the JAR file has to be listed specifically in
      # the JAR manifest as something that goes in the bootclasspath.
      # The MANIFEST list a jar 'allocation.jar' this is why we have to rename it
      updated, classpath = profile_classpath(self.agent_profile)
      agent_jar = os.readlink(classpath[0])
      allocation_jar = os.path.join(os.path.dirname(agent_jar), "allocation.jar")
      if updated:
        shutil.copyfile(agent_jar, allocation_jar)
      os.environ['ALLOCATION_JAR'] = str(allocation_jar)

    if context.options.debug:
      self.jvm_args.extend(context.config.getlist('jvm', 'debug_args'))
      self.caliper_args += ['--debug']

    self.caliper_args.extend(context.options.extra_caliper_args)

  def execute(self, targets):
    caliper_main = 'com.google.caliper.Runner'
    _, classpath = profile_classpath(self.profile)
    exit_code = runjava(self.classpath(classpath, confs=self.confs),
                        caliper_main,
                        args=self.caliper_args,
                        jvm_args=self.jvm_args)
    if exit_code != 0:
      raise TaskError('java %s ... exited non-zero (%i)' % (caliper_main, exit_code))
