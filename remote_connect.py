import paramiko

REMOTE=paramiko.SSHClient()
REMOTE.set_missing_host_key_policy(paramiko.AutoAddPolicy())
REMOTE.connect(
                hostname="MPCRBC-GRED-077",
                username="mougeotg",
                password="")

_,stdout,stderr=REMOTE.exec_command("source /opt/conda/bin/activate; cd /home/mougeotg/all/tmp/biom3d;  python -m biom3d.preprocess --img_dir data/nucleus_0001/img --msk_dir data/nucleus_0001/msk --num_classes 1 --remote")

print(stdout.readlines())

while True:
    line = stderr.readline()
    if not line:
        break
    print(line, end="")