from __future__ import print_function
import sys,os
sum=0
def visit(path,prex="",feature=print,istop=True):
    '''
	[path] is the path you want to visit
	[prex] is the suffix you want to filter, the default is "", that is means visit all 
	[feature] is the function you want to call, default to call the print function and print all the file name with the path,and you cant use it to call you own function 
	[is top] to check the call is the top level, you may not use it 
	eg. you can can is like this -- visit(".","py",lines)
	and if you just import visitor you can write like this -- visitor.visit(".","py",visitor.lines)

    '''
    global sum
    global sum_flag
    if(istop):
	sum=0
	sum_flag=False
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
        visit(pwd+y,prex,feature,False)
    if(sum_flag & istop):
        print ("sum is %d"%sum)
def lines(file_name):
    '''
	This functon is to count the line in the file 
	[file_name] is the single file you want to visitor
    '''
    global sum_flag
    sum_flag=True
    linecount=(len(open(file_name).readlines()))   
    #print (linecount)
    print ("%s:%s" % (file_name,linecount))
    return linecount
path="."
visit(path)
#If you have any problem or advice, you can mail to me "hanyueqi123@163.com"