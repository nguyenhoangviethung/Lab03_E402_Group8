import time
import json
import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExecutionMetrics:
    method_name: str  # "Baseline" hoặc "ReAct"
    query: str = ""   # <-- Thêm trường này để hết lỗi
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_steps: int = 0
    tool_calls: List[str] = field(default_factory=list)
    status: str = "success"

    @property
    def latency(self):
        return round(self.end_time - self.start_time, 3)

    @property
    def total_tokens(self):
        return self.total_tokens_input + self.total_tokens_output

    def to_dict(self):
        return {
            "method": self.method_name,
            "query": self.query,
            "latency_s": self.latency,
            "total_tokens": self.total_tokens,
            "input_tokens": self.total_tokens_input,
            "output_tokens": self.total_tokens_output,
            "steps": self.total_steps,
            "tools": self.tool_calls,
            "status": self.status
        }

class ComparisonDashboard:
    """Công cụ tổng hợp để lưu file benchmark"""
    def __init__(self, save_path="logs/benchmark_results.json"):
        self.results: List[ExecutionMetrics] = []
        self.save_path = save_path
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

    def add_metric(self, metric: ExecutionMetrics):
        self.results.append(metric)

    def save_to_file(self):
        # Đọc dữ liệu cũ nếu có để ghi nối tiếp (append)
        existing_data = []
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

        existing_data.extend([r.to_dict() for r in self.results])

        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)