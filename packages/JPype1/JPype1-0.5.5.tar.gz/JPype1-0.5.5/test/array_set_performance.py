import yep
from jpype import *
import numpy as np
startJVM(getDefaultJVMPath())
n = 10**7
a = np.zeros(n, dtype=np.int64)
jarr = JArray(JInt, 1)(n)
yep.start()
jarr[0:len(jarr)] = a
yep.stop()
shutdownJVM()
