import gc
import psutil
import os


def check_memory_usage() -> dict:
    """Check current memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        "rss_mb": memory_info.rss / 1024 / 1024,
        "vms_mb": memory_info.vms / 1024 / 1024,
        "percent": process.memory_percent()
    }


def optimize_memory(state: dict) -> dict:
    """Optimize memory usage by clearing large objects"""
    memory_before = check_memory_usage()

    # Clear large intermediate objects that are no longer needed
    keys_to_clear = ["raw_documents", "full_research_results", "intermediate_analysis"]
    optimized_state = state.copy()

    for key in keys_to_clear:
        if key in optimized_state:
            del optimized_state[key]

    # Force garbage collection
    gc.collect()

    memory_after = check_memory_usage()
    print(f"Memory optimized: {memory_before['rss_mb']:.1f}MB -> {memory_after['rss_mb']:.1f}MB")

    return optimized_state


def should_pause_processing(state: dict) -> bool:
    """Check if we should pause processing due to memory constraints"""
    memory_info = check_memory_usage()
    return memory_info["percent"] > 85  # Pause if using >85% memory