filePath = ""
fileName = "TwoCyclesTriangleWave_16Bit4096.bin"
f=open(filePath+fileName,"rb")
num=list(f.read())
print (num)
print (len(num))
f.close()
