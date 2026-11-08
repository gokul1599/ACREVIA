"""
Tests for Edge Vision Benchmark Suite.
"""

from ml.evaluation.benchmark import ArchitectureBenchmarkRunner


def test_benchmark_runner_smoke(tmp_path):
    runner = ArchitectureBenchmarkRunner(
        output_dir=str(tmp_path / "benchmarks"),
        warmup_runs=2,
        timed_runs=5,
        num_classes=4
    )

    result = runner.benchmark_architecture("mobilenet_v3_small")
    
    assert result["architecture"] == "mobilenet_v3_small"
    assert "parameters" in result
    assert result["parameters"]["total_parameters"] > 0
    assert "latency" in result
    assert "onnx_int8_cpu" in result["latency"]
    assert result["latency"]["onnx_int8_cpu"]["median_ms"] > 0
    assert result["file_size"]["int8_onnx_mb"] < 15.0
    assert result["edge_compliant"] is True


def test_benchmark_suite_markdown_summary(tmp_path):
    runner = ArchitectureBenchmarkRunner(
        output_dir=str(tmp_path / "benchmarks"),
        warmup_runs=1,
        timed_runs=3,
        num_classes=3
    )

    suite = runner.run_suite(architectures=["mobilenet_v3_small"])
    assert "mobilenet_v3_small" in suite["benchmarks"]
    assert "markdown_summary" in suite
    assert "| `mobilenet_v3_small` |" in suite["markdown_summary"]
