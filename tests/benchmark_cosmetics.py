import sys
import timeit
from pathlib import Path

# Add src/ to PYTHONPATH programmatically
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ruff: noqa: E402
from weaponassambly.registry import cosmetic_allowed, cosmetic_kinds


def benchmark():
    # Warm up
    cosmetic_kinds()
    cosmetic_allowed("finish", "polished_black", "BM-S7")

    # Time cosmetic_kinds (called 10000 times)
    kinds_time = timeit.timeit("cosmetic_kinds()", globals=globals(), number=10000)

    # Time cosmetic_allowed with platform (called 10000 times)
    allowed_with_plat_time = timeit.timeit(
        'cosmetic_allowed("finish", "polished_black", "BM-S7")',
        globals=globals(),
        number=10000
    )

    # Time cosmetic_allowed without platform (called 10000 times)
    allowed_no_plat_time = timeit.timeit(
        'cosmetic_allowed("finish", "polished_black")',
        globals=globals(),
        number=10000
    )

    print(f"cosmetic_kinds: {kinds_time:.6f} seconds for 10000 runs")
    print(f"cosmetic_allowed (with platform): {allowed_with_plat_time:.6f} seconds for 10000 runs")
    print(f"cosmetic_allowed (without platform): {allowed_no_plat_time:.6f} seconds for 10000 runs")


if __name__ == "__main__":
    benchmark()
