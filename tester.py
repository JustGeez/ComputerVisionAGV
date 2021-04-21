import lineTracker as LT
import edgeWirtual as EW
import threading

#threading.Thread(target=LT.main()).start()

p2 = threading.Thread(target=EW.program())
p2.start()
import time
time.sleep(10)
p2.terminate()