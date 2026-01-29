import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# SOURCES = {
#     r"E:\annotations": r"D:\au\datasets\camalien\annotations",
#     r"E:\images":      r"D:\au\datasets\camalien\images",
#     r"E:\json":        r"D:\au\datasets\camalien\json",
# }

SOURCES = {
    "/mnt/e/annotations": "/mnt/d/au/datasets/camalien/annotations",
    "/mnt/e/images":      "/mnt/d/au/datasets/camalien/images",
    "/mnt/e/json":        "/mnt/d/au/datasets/camalien/json",
}

MAX_WORKERS = 32
COPY_BUFFER = 1024 * 1024 * 4  # 4 MB
PROGRESS_EVERY = 1000

lock = Lock()
copied = 0
skipped = 0


def needs_copy(src, dst):
    if not os.path.exists(dst):
        return True

    try:
        return os.path.getsize(src) != os.path.getsize(dst)
    except OSError:
        return True


def copy_file(src, dst):
    global copied, skipped

    if not needs_copy(src, dst):
        with lock:
            skipped += 1
            if (copied + skipped) % PROGRESS_EVERY == 0:
                print(f"Copied {copied:,} | Skipped {skipped:,}", flush=True)
        return

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        shutil.copyfileobj(fsrc, fdst, length=COPY_BUFFER)

    with lock:
        copied += 1
        if (copied + skipped) % PROGRESS_EVERY == 0:
            print(f"Copied {copied:,} | Skipped {skipped:,}", flush=True)


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

    print(f"\nDone. Copied {copied:,}, Skipped {skipped:,}")


if __name__ == "__main__":
    main()
