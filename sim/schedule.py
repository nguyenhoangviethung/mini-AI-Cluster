import math
import random
from typing import Dict, List

from sim.cluster import Cluster
from sim.models import Job, JobStatus, NodeState


class MiniSlurm:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster
        self.jobs: Dict[int, Job] = {}
        self.next_job_id = 1000

    def submit(
        self,
        name: str,
        requested_nodes: int,
        gpus_per_node: int,
        global_batch_size: int,
        model_size_b: float,
        total_steps: int,
    ) -> int:
        job = Job(
            job_id=self.next_job_id,
            name=name,
            requested_nodes=requested_nodes,
            gpus_per_node=gpus_per_node,
            global_batch_size=global_batch_size,
            model_size_b=model_size_b,
            total_steps=total_steps,
        )

        self.jobs[job.job_id] = job
        self.next_job_id += 1

        self._try_allocate(job)

        return job.job_id

    def _try_allocate(self, job: Job) -> None:
        candidate_nodes = [
            node
            for node in self.cluster.ready_nodes()
            if node.free_gpus() >= job.gpus_per_node
        ]

        if len(candidate_nodes) < job.requested_nodes:
            job.status = JobStatus.PENDING
            return

        chosen_nodes = candidate_nodes[:job.requested_nodes]

        for node in chosen_nodes:
            node.allocate_gpus(job.gpus_per_node)
            node.state = NodeState.ALLOCATED

        job.allocated_nodes = [node.name for node in chosen_nodes]
        job.status = JobStatus.RUNNING

    def run_one_step(self, job_id: int) -> None:
        job = self.jobs[job_id]

        if job.status != JobStatus.RUNNING:
            return

        world_size = job.requested_nodes * job.gpus_per_node
        single_node = job.requested_nodes == 1

        effective_bandwidth_gbps = 3200 if single_node else 400

        compute_time = (
            job.model_size_b
            * job.global_batch_size
            / (world_size * 4000)
        )

        gradient_payload_gb = job.model_size_b * 0.02

        communication_time = (
            gradient_payload_gb
            / (effective_bandwidth_gbps / 8)
            * math.log2(world_size + 1)
        )

        step_time = (
            compute_time + communication_time
        ) * random.uniform(0.95, 1.08)

        throughput = job.global_batch_size / step_time

        gpu_utilization = 100 * compute_time / (
            compute_time + communication_time
        )

        for node_name in job.allocated_nodes:
            node = self.cluster.get_node(node_name)

            for gpu in node.gpus:
                if gpu.allocated:
                    gpu.update_telemetry(gpu_utilization)

        job.current_step += 1

        job.history.append({
            "step": job.current_step,
            "world_size": world_size,
            "compute_time_s": round(compute_time, 4),
            "communication_time_s": round(communication_time, 4),
            "step_time_s": round(step_time, 4),
            "throughput_samples_s": round(throughput, 2),
            "gpu_utilization_pct": round(gpu_utilization, 2),
        })

        if job.current_step >= job.total_steps:
            self._complete(job)

    def run_until_done(self, job_id: int) -> None:
        while self.jobs[job_id].status == JobStatus.RUNNING:
            self.run_one_step(job_id)

    def _complete(self, job: Job) -> None:
        job.status = JobStatus.COMPLETED

        for node_name in job.allocated_nodes:
            node = self.cluster.get_node(node_name)
            node.release_all_gpus()
            node.state = NodeState.READY

    def squeue(self) -> List[dict]:
        rows = []

        for job in self.jobs.values():
            rows.append({
                "JOBID": job.job_id,
                "NAME": job.name,
                "STATE": job.status.value,
                "NODES": job.requested_nodes,
                "GPUS_PER_NODE": job.gpus_per_node,
                "STEP": f"{job.current_step}/{job.total_steps}",
            })

        return rows

    def seff_like_report(self, job_id: int) -> dict:
        job = self.jobs[job_id]

        if not job.history:
            return {
                "job_id": job.job_id,
                "error": "Job chưa có metric"
            }

        avg_throughput = sum(
            item["throughput_samples_s"]
            for item in job.history
        ) / len(job.history)

        avg_gpu_utilization = sum(
            item["gpu_utilization_pct"]
            for item in job.history
        ) / len(job.history)

        avg_communication_time = sum(
            item["communication_time_s"]
            for item in job.history
        ) / len(job.history)

        avg_step_time = sum(
            item["step_time_s"]
            for item in job.history
        ) / len(job.history)

        communication_overhead_pct = (
            100 * avg_communication_time / avg_step_time
        )

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "avg_throughput_samples_s": round(avg_throughput, 2),
            "avg_gpu_utilization_pct": round(avg_gpu_utilization, 2),
            "avg_communication_overhead_pct": round(communication_overhead_pct, 2),
        }