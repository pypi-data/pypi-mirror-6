from jpype import *
startJVM(getDefaultJVMPath())
jarr = JArray(JFloat, 1)(10)
try:
    jarr[1:2] = [dict()] # incompatible
except Exception as e:
    print type(e), e
print jarr
#jarr[1:2] = (())
shutdownJVM()
