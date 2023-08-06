# ==================================================================================================
# Copyright 2014 Twitter, Inc.
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

from twitter.pants.base.build_manual import manual
from twitter.pants.targets.exclude import Exclude
from twitter.pants.targets.jvm_target import JvmTarget
from twitter.pants.targets.hadoop_binary import ON_HADOOP_CLUSTER_EXCLUDES

OINK_EXCLUDES = ON_HADOOP_CLUSTER_EXCLUDES + [
  Exclude('org.apache.pig'),
  Exclude('org.apache.hbase', 'hbase')
]

@manual.builddict(tags=["jvm"])
class OinkQuery(JvmTarget):
  """Represents an OinkQuery target.

  Goals such as ``bundle`` will create a OinkQuery bundle.
  """

  def __init__(self, name, dependencies, sources=None, excludes=None, deploy_excludes=None):
    """
    :param string name: The name of this target, which combined with this
      build file defines the target :class:`twitter.pants.base.address.Address`.
    :param dependencies: List of targets (probably ``java_library`` targets
      to "link" in.
    :param string sources: Optional list of ``.yml`` files that represent the
      Oink Query job.
    :param excludes: List of ``exclude``\s to filter this target's transitive
      dependencies against.
    :param deploy_excludes: List of ``excludes`` to apply at deploy time.
      If you, for example, deploy a a servlet that has one version of
      ``servlet.jar`` onto a Tomcat environment that provides another version,
      they might conflict. ``deploy_excludes`` gives you a way to build your
      code but exclude the conflicting ``jar`` when deploying.
    """
    JvmTarget.__init__(self, name, sources, dependencies, excludes)
    # TODO: configurations is required when fetching jar_dependencies but should not be
    self.configurations = None
    self.deploy_excludes = (deploy_excludes or []) + OINK_EXCLUDES
