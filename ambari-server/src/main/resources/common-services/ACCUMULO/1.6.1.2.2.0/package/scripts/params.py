#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import hdp_select
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import format
from resource_management.libraries.functions.version import format_hdp_stack_version
from resource_management.libraries.functions.default import default
from resource_management.libraries.script.script import Script

import status_params

# server configurations
config = Script.get_config()
exec_tmp_dir = status_params.tmp_dir

# security enabled
security_enabled = status_params.security_enabled

# hdp version
stack_name = default("/hostLevelParams/stack_name", None)
version = default("/commandParams/version", None)
stack_version_unformatted = str(config['hostLevelParams']['stack_version'])
hdp_stack_version = format_hdp_stack_version(stack_version_unformatted)

has_secure_user_auth = False
if Script.is_hdp_stack_greater_or_equal("2.3"):
  has_secure_user_auth = True

# configuration directories
conf_dir = status_params.conf_dir
server_conf_dir = status_params.server_conf_dir

# service locations
hadoop_prefix = hdp_select.get_hadoop_dir("home")
hadoop_bin_dir = hdp_select.get_hadoop_dir("bin")
zookeeper_home = "/usr/hdp/current/zookeeper-client"

# the configuration direction for HDFS/YARN/MapR is the hadoop config
# directory, which is symlinked by hadoop-client only
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()

# accumulo local directory structure
log_dir = config['configurations']['accumulo-env']['accumulo_log_dir']
client_script = "/usr/hdp/current/accumulo-client/bin/accumulo"
daemon_script = format("ACCUMULO_CONF_DIR={server_conf_dir} {client_script}")

# user and status
accumulo_user = status_params.accumulo_user
user_group = config['configurations']['cluster-env']['user_group']
pid_dir = status_params.pid_dir

# accumulo env
java64_home = config['hostLevelParams']['java_home']
accumulo_master_heapsize = config['configurations']['accumulo-env']['accumulo_master_heapsize']
accumulo_tserver_heapsize = config['configurations']['accumulo-env']['accumulo_tserver_heapsize']
accumulo_monitor_heapsize = config['configurations']['accumulo-env']['accumulo_monitor_heapsize']
accumulo_gc_heapsize = config['configurations']['accumulo-env']['accumulo_gc_heapsize']
accumulo_other_heapsize = config['configurations']['accumulo-env']['accumulo_other_heapsize']
accumulo_monitor_bind_all = config['configurations']['accumulo-env']['accumulo_monitor_bind_all']
monitor_bind_str = "false"
if accumulo_monitor_bind_all:
  monitor_bind_str = "true"
env_sh_template = config['configurations']['accumulo-env']['content']
server_env_sh_template = config['configurations']['accumulo-env']['server_content']

# accumulo initialization parameters
instance_name = config['configurations']['accumulo-env']['accumulo_instance_name']
instance_secret = config['configurations']['accumulo-env']['instance_secret']
root_password = config['configurations']['accumulo-env']['accumulo_root_password']
instance_volumes = config['configurations']['accumulo-site']['instance.volumes']
parent_dir = instance_volumes[0:instance_volumes.rfind('/')]

# tracer properties
trace_user = config['configurations']['accumulo-site']['trace.user']
trace_password = config['configurations']['accumulo-env']['trace_password']

# credential provider
credential_provider = parent_dir.replace("hdfs://", "jceks://hdfs@") + "/accumulo-site.jceks"

# smoke test
smoke_test_user = config['configurations']['cluster-env']['smokeuser']
smoke_test_password = 'smoke'
smokeuser_principal =  config['configurations']['cluster-env']['smokeuser_principal_name']
smoke_user_keytab = config['configurations']['cluster-env']['smokeuser_keytab']

# log4j.properties
log4j_props = config['configurations']['accumulo-log4j']['content']
audit_log_level = config['configurations']['accumulo-log4j']['audit_log_level']
monitor_forwarding_log_level = config['configurations']['accumulo-log4j']['monitor_forwarding_log_level']
debug_log_size = config['configurations']['accumulo-log4j']['debug_log_size']
debug_num_logs = config['configurations']['accumulo-log4j']['debug_num_logs']
info_log_size = config['configurations']['accumulo-log4j']['info_log_size']
info_num_logs = config['configurations']['accumulo-log4j']['info_num_logs']

# metrics2 properties
ganglia_server_hosts = default('/clusterHostInfo/ganglia_server_host', []) # is not passed when ganglia is not present
ganglia_server_host = '' if len(ganglia_server_hosts) == 0 else ganglia_server_hosts[0]
ams_collector_hosts = default("/clusterHostInfo/metrics_collector_hosts", [])
has_metric_collector = not len(ams_collector_hosts) == 0
if has_metric_collector:
  metric_collector_host = ams_collector_hosts[0]
  metric_collector_port = default("/configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:6188")
  if metric_collector_port and metric_collector_port.find(':') != -1:
    metric_collector_port = metric_collector_port.split(':')[1]
  pass

metrics_report_interval = default("/configurations/ams-site/timeline.metrics.sink.report.interval", 60)
metrics_collection_period = default("/configurations/ams-site/timeline.metrics.sink.collection.period", 60)

# if accumulo is selected accumulo_tserver_hosts should not be empty, but still default just in case
if 'slave_hosts' in config['clusterHostInfo']:
  tserver_hosts = default('/clusterHostInfo/accumulo_tserver_hosts', '/clusterHostInfo/slave_hosts')
else:
  tserver_hosts = default('/clusterHostInfo/accumulo_tserver_hosts', '/clusterHostInfo/all_hosts')
master_hosts = default('/clusterHostInfo/accumulo_master_hosts', [])
monitor_hosts = default('/clusterHostInfo/accumulo_monitor_hosts', [])
gc_hosts = default('/clusterHostInfo/accumulo_gc_hosts', [])
tracer_hosts = default('/clusterHostInfo/accumulo_tracer_hosts', [])

# security properties
accumulo_user_keytab = config['configurations']['accumulo-env']['accumulo_user_keytab']
accumulo_principal_name = config['configurations']['accumulo-env']['accumulo_principal_name']

# kinit properties
kinit_path_local = status_params.kinit_path_local
if security_enabled:
  kinit_cmd = format("{kinit_path_local} -kt {accumulo_user_keytab} {accumulo_principal_name};")
else:
  kinit_cmd = ""

host_sys_prepped = default("/hostLevelParams/host_sys_prepped", False)

#for create_hdfs_directory
hostname = status_params.hostname
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']



hdfs_site = config['configurations']['hdfs-site']
default_fs = config['configurations']['core-site']['fs.defaultFS']

dfs_type = default("/commandParams/dfs_type", "")

# dfs.namenode.https-address
import functools
#create partial functions with common arguments for every HdfsResource call
#to create/delete hdfs directory/file/copyfromlocal we need to call params.HdfsResource in code
HdfsResource = functools.partial(
  HdfsResource,
  user=hdfs_user,
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  hadoop_bin_dir = hadoop_bin_dir,
  hadoop_conf_dir = hadoop_conf_dir,
  principal_name = hdfs_principal_name,
  hdfs_site = hdfs_site,
  default_fs = default_fs,
  dfs_type = dfs_type
)
