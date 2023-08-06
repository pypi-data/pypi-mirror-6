import random
import argparse

import json
import gevent
import etcd
import uuid

from subprocess import Popen, PIPE, STDOUT

from crow.agent.config import AgentConfig

TTL = 3
TTL_OFFSET = 2

class CLI(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser(description='Client version management over ETCD.')

  def add_subparsers(self, *args, **kwargs):
    return self.parser.add_subparsers(*args, **kwargs)

  def add_param(self, *args, **kwargs):
    return self.parser.add_argument(*args, **kwargs)

  def add_argument(self, *args, **kwargs):
    return self.parser.add_argument(*args, **kwargs)

  def run(self):
    self.params = self.parser.parse_args()
    self.main()

class AgentBase(object):

  def __init__(self, name, peers, config_path, cluster):
    self.peers = peers
    self.cluster = cluster

    self.name = "%s.%s" % (name, uuid.uuid4().hex)

    self.config = AgentConfig.from_file(config_path)

  def _get_client(self):
    peer = random.sample(self.peers, 1)[0]
    host, port = peer.split(":")

    return etcd.Client(host=host, port=port)

  def run(self):
    greenlets = []

    greenlets.append(gevent.spawn(self.watcher))
    greenlets.append(gevent.spawn(self.heartbeat))

    [ g.join() for g in greenlets ]

  def heartbeat(self):
    client = self._get_client()

    metadata = json.dumps(self.config["metadata"])

    client.set("crow/clusters/%s/%s" % (self.cluster, self.name),
               metadata, full_response=True, ttl=TTL + TTL_OFFSET)

    gevent.sleep(TTL)

    while True:
      client.refresh("crow/clusters/%s/%s" % (self.cluster, self.name), value=metadata, ttl=TTL + TTL_OFFSET)
      gevent.sleep(TTL)

  def handler(self, command, metadata):
    print "Handler", command
    p = Popen([command], shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    p.communicate(input=json.dumps(metadata))

  def watcher(self):
    client = self._get_client()

    for item in client.watch("crow/clusters/%s" % self.cluster, recursive=True):
      print item
      if item['node']['key'] == "/crow/clusters/%s/%s" % (self.cluster, self.name):
        continue

      if item['action'] == "set":
        gevent.spawn(self.handler, self.config["handlers"]["member_join"], item)

      if item['action'] == "expire":
        gevent.spawn(self.handler, self.config["handlers"]["member_leave"], item)

class AgentBaseCLI(CLI):

  def main(self):
    agent = AgentBase(
      name=self.params.name,
      peers=self.params.peers,
      config_path=self.params.config,
      cluster=self.params.cluster
    )

    agent.run()
