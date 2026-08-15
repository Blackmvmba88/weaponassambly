import time

from weaponassambly.registry import cosmetic_allowed, cosmetic_kinds


def benchmark():
    print("Starting micro-benchmark...")
    # Warm up
    for _ in range(100):
        cosmetic_kinds()
        cosmetic_allowed("finish", "polished_black", "BM-S7")
        cosmetic_allowed("finish", "invalid_value", "BM-S7")
        cosmetic_allowed("finish", "polished_black", None)

    # Measure cosmetic_kinds
    start = time.perf_counter()
    for _ in range(100000):
        cosmetic_kinds()
    end = time.perf_counter()
    kinds_time = end - start
    print(f"cosmetic_kinds time (100,000 iterations): {kinds_time:.6f}s")

    # Measure cosmetic_allowed
    start = time.perf_counter()
    for _ in range(100000):
        cosmetic_allowed("finish", "polished_black", "BM-S7")
        cosmetic_allowed("finish", "invalid_value", "BM-S7")
        cosmetic_allowed("finish", "polished_black", None)
    end = time.perf_counter()
    allowed_time = end - start
    print(f"cosmetic_allowed time (100,000 iterations): {allowed_time:.6f}s")

if __name__ == "__main__":
    benchmark()
