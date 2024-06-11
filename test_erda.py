import os
from pyremotedata.implicit_mount import IOHandler
 
os.environ["PYREMOTEDATA_REMOTE_USERNAME"] = "gmo@ecos.au.dk"
os.environ["PYREMOTEDATA_REMOTE_URI"] = "io.erda.au.dk"
os.environ["PYREMOTEDATA_REMOTE_DIRECTORY"] = "/"
os.environ["PYREMOTEDATA_AUTO"] = "yes"

# Print pyremotedata environment variables
pyremote_evars = [
    "PYREMOTEDATA_REMOTE_USERNAME",
    "PYREMOTEDATA_REMOTE_URI",
    "PYREMOTEDATA_REMOTE_DIRECTORY",
    "PYREMOTEDATA_AUTO"
]
 
for evar in pyremote_evars:
    print(f'{evar}={os.environ[evar]}')
 
failed = False
 
# Make sure to set clean=False if you have files you want to keep in the `local_dir` directory
with IOHandler(local_dir=os.getcwd(), clean=False) as io:
    print(io.pwd())
    print(io.ls())
 
    # io.cd("testing")
    if io.ls(use_cache=False) is None or "test_put_url" not in io.ls(use_cache=False):
        io.execute_command("mkdir test_put_url")
    io.cd("test_put_url")
    io.put("https://www.papua-insects.nl/insect%20orders/Lepidoptera/Sphingidae/Hippotion/Hippotion%20boerhaviae%20%5Bksp%5D.jpg", "test.jpg")
    print(io.ls())
    if io.ls(use_cache=False) is None or "test.jpg" in io.ls(use_cache=False):
        downloaded_file = io.download("test.jpg", "test.jpg")
        print(f"File downloaded to {downloaded_file}")
        io.execute_command("rm test.jpg")
    else:
        failed = True
        print("File not found after put")
    if not io.ls(use_cache=False) is None and "test.jpg" in io.ls(use_cache=False):
        failed = True
        print("File not removed after rm")
    else:
        io.cd("..")
        io.execute_command("rmdir test_put_url")
 
if not "test.jpg" in os.listdir("."):
    failed = True
    print("File not found after download")
 
if failed:
    print("Test failed")
else:
    print("Test passed")