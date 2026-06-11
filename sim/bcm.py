from typing import Dict, List
from sim.models import Node, NodeState
from sim.cluster import Cluster

class miniBCM:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster
    
        self.sofeware_images = {
            "dxg-base": {
                "os": "Ubuntu",
                "cuda": "sim",
                "driver": "sim",
                "pytorch": "sim"
            }
        }
    
        self.categories = Dict[str, str]

    def clone_image(self, base_image: str, new_image: str):
        if base_image not in self.sofeware_images:
            raise ValueError(f"Base image not found: {base_image}")
        
        self.sofeware_images[new_image] = self.sofeware_images[base_image].copy()   
    
    def create_category(self, category_name: str, software_image: str):
        if software_image not in self.sofeware_images:
            raise ValueError(f"Image not found: {software_image}")
        
        self.categories[category_name] = software_image

    def provision_node(self, node_name: str, category_name: str):
        if category_name not in self.categories:
            raise ValueError(f"Category not found: {category_name}")
        
        node = self.cluster.get_node(node_name)
        node.category = category_name
        node.software_image = self.categories[category_name]
        node.state = NodeState.READY
    
    def cluster_status(self) -> Dict[str, Dict]:
        row = []

        for node in self.cluster.nodes.values():
            row.append({
                "name": node.name,
                "state": node.state,
                "category": node.category,
                "software_image": node.software_image,
                "free_gpus": node.free_gpus()
            })
        return row

    def gpu_telemetry(self) -> List[Dict]:
        telemetry = []

        for node in self.cluster.nodes.values():
            for gpu in node.gpus:
                telemetry.append({
                    "node": node.name,
                    "gpu_id": gpu.local_id,
                    "utilization": gpu.utilization,
                    "power_w": gpu.power_w,
                    "temperature_c": gpu.temperature_c,
                    "allocated": gpu.allocated
                })
        
        return telemetry