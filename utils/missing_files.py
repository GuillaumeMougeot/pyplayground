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

# =========================================================
# FIND MISSING FILES
# =========================================================

with open(JSON_FILE, "r", encoding="utf-8") as f:
    tasks = json.load(f)

missing = []

for item in tasks:
    video_path = item["data"]["video"]

    relative_path = video_path.replace(
        "/data/local-files/?d=TestDataset/Selection/",
        ""
    )

    local_path = LOCAL_BASE / relative_path

    if not local_path.exists():
        remote_path = f"Data_backup/{relative_path}"
        missing.append((remote_path, local_path))

print(f"Missing files: {len(missing)}")

for remote, local in missing:
    print(f"Will download:\n  {remote}\n  -> {local}")

# =========================================================
# DOWNLOAD MISSING FILES
# =========================================================

async def main():
    async with asyncssh.connect(
        SFTP_HOST,
        port=SFTP_PORT,
        username=SFTP_USER,
        password=SFTP_PASSWORD,
        known_hosts=None,
    ) as conn:

        async with conn.start_sftp_client() as sftp:

            for remote_path, local_path in missing:

                local_path.parent.mkdir(parents=True, exist_ok=True)

                try:
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

asyncio.run(main())
