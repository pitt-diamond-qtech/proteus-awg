filePath = ""
fileName = "TwoCyclesTriangle_16Bit4096pts.bin"
f=open(filePath+fileName,"rb")
num=list(f.read())
print (num)
print (len(num))
f.close()
