import yaml

class AgentConfig(object):

  @classmethod
  def from_file(cls, path):
    with open(path, "r") as fp:
      return yaml.load(fp.read())
