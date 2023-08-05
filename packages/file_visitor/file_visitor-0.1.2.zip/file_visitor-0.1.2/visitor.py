from __future__ import print_function
import sys,os
sum=0
sum_flag=False
def fileCheck(path,prex="",feature=print,istop=True):
    global sum
    global sum_flag
    now = os.walk(path).next();
    files = now[2]
    dirs=now[1]
    pwd=now[0]+"\\"
    for x in files:
        if(prex==""):
            result=feature(pwd+x)
            if(sum_flag==True):
                sum=sum+result
        else:
            file_prex=x.split(".")[-1]
            #print file_prex
            if(file_prex==prex):
                 result=feature(pwd+x)
                 if(sum_flag==True):
                    sum=sum+result
    for y in dirs:
        fileCheck(pwd+y,prex,feature,False)
    if(sum_flag & istop):
        print ("sum is %d"%sum)
def lines(file_name):
    global sum_flag
    sum_flag=True
    linecount=(len(open(file_name).readlines()))   
    #print (linecount)
    print ("%s:%s" % (file_name,linecount))
    return linecount
#path="."
#fileCheck(path,"py",lines)