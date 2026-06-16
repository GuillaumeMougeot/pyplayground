import asyncio
import json
from pathlib import Path

import asyncssh

# =========================================================
# CONFIG
# =========================================================

JSON_FILE = "Selection.json"

SFTP_HOST = "io.erda.au.dk"
SFTP_PORT = 2222
SFTP_USER = <USER>
SFTP_PASSWORD = <PWD>

LOCAL_BASE = Path("/home/wildcam/labelstudio-data/selection")

# Number of concurrent downloads
CONCURRENT_DOWNLOADS = 16

# =========================================================
# LOAD TASKS
# =========================================================

with open(JSON_FILE, "r", encoding="utf-8") as f:
    tasks = json.load(f)

downloads = []

for item in tasks:
    video_path = item["data"]["video"]

    # Remove Label Studio prefix
    relative_path = video_path.replace(
        "/data/local-files/?d=TestDataset/Selection/",
        "",
    )

    remote_path = f"Data_backup/{relative_path}"

    local_path = LOCAL_BASE / relative_path

    downloads.append((remote_path, local_path))

print(f"Found {len(downloads)} files")

# =========================================================
# ASYNC DOWNLOAD
# =========================================================

sem = asyncio.Semaphore(CONCURRENT_DOWNLOADS)


async def download_file(sftp, remote_path, local_path):
    async with sem:
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Skip existing files
            if local_path.exists():
                print(f"[SKIP] {local_path}")
                return

            print(f"[DOWN] {remote_path}")

            await sftp.get(
                remote_path,
                str(local_path),
                preserve=True,
            )

            print(f"[DONE] {local_path}")

        except FileNotFoundError:
            print(f"[MISS] {remote_path}")

        except Exception as e:
            print(f"[ERR ] {remote_path} -> {e}")


async def main():
    async with asyncssh.connect(
        SFTP_HOST,
        port=SFTP_PORT,
        username=SFTP_USER,
        password=SFTP_PASSWORD,
        known_hosts=None,  # equivalent to StrictHostKeyChecking=no
    ) as conn:

        async with conn.start_sftp_client() as sftp:

            await asyncio.gather(
                *[
                    download_file(sftp, remote, local)
                    for remote, local in downloads
                ]
            )


if __name__ == "__main__":
    asyncio.run(main())
