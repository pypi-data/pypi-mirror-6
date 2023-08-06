from crow.agent import AgentBaseCLI

def execute_from_cli():
  agent = AgentBaseCLI()

  agent.add_argument("--name", action='store', type=str, default="croco", help="Name of node")
  agent.add_argument("--config", action='store', type=str, default="/etc/crow/crow.conf", help="Path to config")
  agent.add_argument("--cluster", default="prod", help="Cluster to watch")
  agent.add_argument("--peers", "-C", nargs="*", default=["localhost:4001"], action='store', type=str, help="List of peers for the etcd cluster")

  agent.run()

