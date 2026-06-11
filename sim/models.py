from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import math
import random
import json

class NodeState(str, Enum):
    BARE_METAL = "BARE_METAL"
    IMAGING = "IMAGING"
    READY = "READY"
    ALLOCATED = "ALLOCATED"
    DOWN = "DOWN"

class JobState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
@dataclass
class GPU:
    local_id: int
    model: str = "SIM_GPU"
    memory_gb: int = 100
    utilization: float = 0.0 
    power_w : float = 70.0
    tempature_c: float = 30.0
    allocated: bool = False

    def update_telemetry(self, util: float):
        self.utilization = max(0.0, min(100.0, util))
        self.power_w = 70.0 + 3.2 * self.utilization + random.uniform(-4, 4)
        self.temperature_c = 35.0 + 0.42 * self.utilization + random.uniform(-1.5, 1.5)
    

@dataclass
class Node:
    name: str
    rack: str
    gpus: List[GPU] = field(default_factory=lambda: [GPU(local_id=i) for i in range(8)])
    state: NodeState = NodeState.BARE_METAL
    category: Optional[str] = None
    software_image: Optional[str] = None

    def free_gpus(self) -> int:
        return sum(1 for gpu in self.gpus if not gpu.allocated)
    
    def allocate_gpus(self, count: int) -> List[GPU]:
        free = [gpu for gpu in self.gpus if not gpu.allocated]    

        if len(free) < count:
            raise ValueError(f"Not enough free GPUs on node {self.name}. Requested: {count}, Available: {len(free)}")
        
        selected = free[:count]
        for gpu in selected:
            gpu.allocated = True

        return selected
    
    def release_gpus(self, gpus: List[GPU]):
        for gpu in gpus:
            gpu.allocated = False
            gpu.update_telemetry(0.0)

@dataclass
class Job:
    job_id: str
    name: str
    requested_nodes: int 
    gpu_per_node: int
    global_batch_size: int
    model_size_b: float
    total_steps: int 

    state: JobState = JobState.PENDING
    allocated_nodes: List[Node] = field(default_factory=list)
    current_step: int = 0
    history: List[dict] = field(default_factory=list)