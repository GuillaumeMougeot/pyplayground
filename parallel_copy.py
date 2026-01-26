import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

# ==========================
# CONFIG
# ==========================
SOURCES = {
    r"E:\annotations": r"D:\au\datasets\camalien\annotations",
    r"E:\images":      r"D:\au\datasets\camalien\images",
    r"E:\json":        r"D:\au\datasets\camalien\json",
}

MAX_WORKERS = 32          # try 32–64 for SSD/NVMe
COPY_BUFFER = 1024 * 1024 * 4  # 4 MB
PROGRESS_EVERY = 1000

# ==========================
# INTERNALS
# ==========================
lock = Lock()
copied = 0


def copy_file(src, dst):
    global copied
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        shutil.copyfileobj(fsrc, fdst, length=COPY_BUFFER)

    with lock:
        copied += 1
        if copied % PROGRESS_EVERY == 0:
            print(f"Copied {copied:,} files", flush=True)


def enumerate_files(src_root, dst_root):
    for root, _, files in os.walk(src_root):
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, src_root)
            dst = os.path.join(dst_root, rel)
            yield src, dst


def main():
    tasks = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for src_root, dst_root in SOURCES.items():
            for src, dst in enumerate_files(src_root, dst_root):
                tasks.append(executor.submit(copy_file, src, dst))

        for _ in as_completed(tasks):
            pass

    print(f"\nDone. Copied {copied:,} files total.")


if __name__ == "__main__":
    main()
