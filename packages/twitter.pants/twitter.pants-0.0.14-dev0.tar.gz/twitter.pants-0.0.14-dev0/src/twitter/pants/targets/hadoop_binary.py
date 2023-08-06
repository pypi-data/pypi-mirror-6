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

from twitter.pants.targets.exclude import Exclude
from twitter.pants.targets.jvm_binary import JvmBinary

# The hadoop cluster provides the appropriate versions of these jars.
ON_HADOOP_CLUSTER_EXCLUDES = [
  Exclude('commons-httpclient','commons-httpclient'),
  Exclude('org.apache', 'hadoop-core'),
  Exclude('org.apache', 'hadoop-lzo'),
  Exclude('com.hadoop', 'hadoop-lzo'),
  Exclude('org.apache.hadoop')
]

class TwitterHadoopBinary(JvmBinary):
  """A binary that is suitable for running on the Hadoop cluster.

  Invoking the ``binary`` or ``bundle`` goal on one of these targets creates a binary jar that
  excludes any dependencies already provided by the hadoop cluster.
  """
  def __init__(
      self,
      name,
      main,
      basename=None,
      source=None,
      resources=None,
      dependencies=None,
      excludes=[],
      deploy_excludes=[]):

    JvmBinary.__init__(
      self,
      name=name,
      main=main,
      basename=basename,
      source=source,
      resources=resources,
      dependencies=dependencies,
      excludes=excludes,
      deploy_excludes=(deploy_excludes or []) + ON_HADOOP_CLUSTER_EXCLUDES,
      configurations=None
    )
