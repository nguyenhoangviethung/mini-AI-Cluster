from dataclasses import dataclass
from typing import Dict, List

from sim.models import Node, NodeState


@dataclass
class Cluster:
    nodes: Dict[str, Node]

    @classmethod
    def make_demo_cluster(cls, num_nodes: int = 4) -> "Cluster":
        nodes = {}

        for idx in range(1, num_nodes + 1):
            node_name = f"dgx{idx:03d}"
            rack_name = f"rack{1 + (idx - 1) // 2}"

            nodes[node_name] = Node(
                name=node_name,
                rack=rack_name
            )

        return cls(nodes=nodes)

    def ready_nodes(self) -> List[Node]:
        return [
            node
            for node in self.nodes.values()
            if node.state == NodeState.READY
        ]

    def get_node(self, node_name: str) -> Node:
        if node_name not in self.nodes:
            raise ValueError(f"Node not found: {node_name}")

        return self.nodes[node_name]