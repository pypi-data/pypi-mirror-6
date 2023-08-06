import os
sup_lst=["com.sp.protector","com.sp.protector.free","com.thinkyeah.smartlockfree","com.thinkyeah.smartlock"]
print("KILL LCK by +Kaveen Rodrigo")
achecks = os.popen("adb version").read()
if (achecks[0:6]=="Androi"):
	print("ADB DETECTED")
else:
	print ("NO ADB INSTALLED")
	exit()
pls = os.popen("adb shell ps").read()
if (pls[0:3]=="USE"):
	print("LISTING OK")
else:
	print("LISTING FAILED")
	exit()
pls_l = pls.split("\n")
for i in pls_l:
	lst= i.split(" ")
	if lst[-1] in sup_lst:
		print("GOT IT "+lst[-1])
		s_ss = os.popen("adb shell pm clear "+ lst[-1]).read()
		print("BOOM - "+s_ss+" "+lst[-1])
exit()
