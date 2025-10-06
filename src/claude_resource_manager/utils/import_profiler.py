"""Import profiling utility for performance analysis.

Tracks import times to identify bottlenecks during module loading.
"""

import time
from typing import Dict, Optional


class ImportProfiler:
    """Context manager to profile module import times.

    Example:
        with ImportProfiler() as profiler:
            import expensive_module

        report = profiler.get_report()
        print(f"Total time: {report['total_time']:.3f}s")
    """

    def __init__(self):
        """Initialize import profiler."""
        self.import_times: Dict[str, float] = {}
        self.total_time = 0.0
        self._start_time: Optional[float] = None
        self._original_import = None

    def __enter__(self):
        """Start profiling imports."""
        self._start_time = time.perf_counter()
        self._original_import = __builtins__["__import__"]

        def profiling_import(name, *args, **kwargs):
            """Wrapper for __import__ that tracks timing."""
            import_start = time.perf_counter()
            try:
                module = self._original_import(name, *args, **kwargs)
                return module
            finally:
                import_duration = time.perf_counter() - import_start

                # Only track if significant (>1ms)
                if import_duration > 0.001:
                    if name in self.import_times:
                        self.import_times[name] += import_duration
                    else:
                        self.import_times[name] = import_duration

        __builtins__["__import__"] = profiling_import
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop profiling and restore original import."""
        __builtins__["__import__"] = self._original_import
        self.total_time = time.perf_counter() - (self._start_time or 0)
        return False

    def get_report(self) -> Dict:
        """Get profiling report.

        Returns:
            Dict with total_time and imports breakdown
        """
        # Sort imports by time (slowest first)
        sorted_imports = sorted(self.import_times.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_time": self.total_time,
            "imports": [{"module": name, "time": duration} for name, duration in sorted_imports],
            "slow_imports": [name for name, duration in sorted_imports if duration > 0.01],  # >10ms
        }

    def print_report(self, top_n: int = 10):
        """Print formatted profiling report.

        Args:
            top_n: Number of slowest imports to show
        """
        report = self.get_report()

        print("\n=== Import Profiling Report ===")
        print(f"Total import time: {report['total_time']:.3f}s")
        print(f"\nTop {top_n} slowest imports:")

        for i, import_data in enumerate(report["imports"][:top_n], 1):
            module = import_data["module"]
            duration = import_data["time"]
            print(f"  {i}. {module:40s} {duration*1000:>8.2f}ms")

        slow_count = len(report["slow_imports"])
        if slow_count > 0:
            print(f"\nFound {slow_count} slow imports (>10ms)")
