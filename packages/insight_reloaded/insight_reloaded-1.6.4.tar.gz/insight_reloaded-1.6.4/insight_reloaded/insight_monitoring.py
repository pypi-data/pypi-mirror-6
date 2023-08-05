import requests
import sys

from collections import deque
from time import sleep

url = sys.argv[1]
q = deque(maxlen=int(sys.argv[2]))

while True:
    r = requests.get(url)
    n = r.json()['number_in_queue']
    if q:
        diff = (n - q[0]) / float(len(q))
        print "%s (diff %+d) [%+F/s]" % (n, n - q[0], diff)
    q.append(n)
    sleep(1)
