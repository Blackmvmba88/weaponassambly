import time

from weaponassambly.registry import cosmetic_allowed, cosmetic_kinds


def run_benchmark():
    # Warm up / run once to load everything
    _ = cosmetic_kinds()
    _ = cosmetic_allowed("grip_panel", "serpent_scale", "BM-S7")

    iterations = 10000

    # 1. Benchmark cosmetic_kinds
    start = time.perf_counter()
    for _ in range(iterations):
        _ = cosmetic_kinds()
    end = time.perf_counter()
    kinds_time = (end - start) * 1000
    print(f"cosmetic_kinds ({iterations} iterations): {kinds_time:.4f} ms")

    # 2. Benchmark cosmetic_allowed (with platform)
    start = time.perf_counter()
    for _ in range(iterations):
        _ = cosmetic_allowed("grip_panel", "serpent_scale", "BM-S7")
    end = time.perf_counter()
    allowed_platform_time = (end - start) * 1000
    print(f"cosmetic_allowed with platform: {allowed_platform_time:.4f} ms")

    # 3. Benchmark cosmetic_allowed (without platform)
    start = time.perf_counter()
    for _ in range(iterations):
        _ = cosmetic_allowed("grip_panel", "serpent_scale", None)
    end = time.perf_counter()
    allowed_no_platform_time = (end - start) * 1000
    print(f"cosmetic_allowed without platform: {allowed_no_platform_time:.4f} ms")


if __name__ == "__main__":
    run_benchmark()
