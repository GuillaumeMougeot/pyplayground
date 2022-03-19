import time 

crt_t = time.time()

for _ in range(10):
    while time.time()-crt_t<1:
        1
    crt_t = time.time()
    print('tic')