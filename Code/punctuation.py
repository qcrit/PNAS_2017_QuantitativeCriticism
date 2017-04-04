from __future__ import division
from usefulfunctions import getsenecanames,getpathtoseneca,parse,charcount,plotsinglebargraph
import os
import string
#import pylab
import argparse
import numpy as np
#import matplotlib.pyplot as plt
path_to_data=getpathtoseneca()
def countenj(absfilepath,onlyfirstword=True):
    #(see countenjambments)
	return countenjambments(parse(absfilepath),onlyfirstword)
def countenjambments(parsedlines,onlyfirstword=True):
	#Counts the number of instances of enjambment in an xml file. If onlyfirstword is true, tests for punctuation at the end of the first word of next line. If it's false, tests for punctuation in first half of next line.
    parsedlines=[i for i in parsedlines if not i.isspace()]
    enjcount=0
    for i in range(1,len(parsedlines)):
        if onlyfirstword:
            temp1=mysplit(parsedlines[i]," ")[0][-1]
            temp2=mysplit(parsedlines[i-1]," ")[-1][-1]
            if mysplit(parsedlines[i]," ")[0][-1] in string.punctuation and not     mysplit(parsedlines[i-1]," ")[-1][-1] in string.punctuation:
                enjcount+=1
        else:
            for j in range(0,int(len(parsedlines[i])/2)):
                if parsedlines[i][j] in string.punctuation and not mysplit(parsedlines[i-1]," ")[-1][-1] in string.punctuation:
                        enjcount+=1
    return enjcount
def countinlinepunc(absfilepath):
	#(see countinlinepuncfromlines)
	return countinlinepuncfromlines(parse(absfilepath))
def countinlinepuncfromlines(listoflines):
	#Counts the total amount of inline punctuation in a list of lines.
	count=0
	for line in listoflines:
		for word in mysplit(line," ")[:-1]:
			marks=[".","?","!",":",";","[","]","-"]
			for mark in marks:
				if mark in word:
					print line
					count+=1
					break
	return count
def countsensepauses(absfilepath,includeends=True):
	#Counts the number of sense-pauses in a given text (possibly buggy at the moment). If includeends is False, only counts in-line sense pauses.
	return countsensepausesfromlines(parse(absfilepath),includeends)
def countsensepausesfromlines(listoflines,includeends):
	count=0
	for line in listoflines:
		temp=mysplit(line," ")
		for word in temp[:len(temp) if includeends else -1]:
			marks=[".","?","!",":",";","[","]","-","\""]
			for mark in marks:
				if mark in word:
					print line
					count+=1
					break

	return count
def mysplit(s,delim=None):
	#A version of the str.split() function that excludes empty strings from the returned list.
	return [x for x in s.split(delim) if x]
def plotmultiple(listofabsxmlfilepaths,onlyfirstword,normalization):
	#Plots the number of instances of enjambment for a list of xml files. The normalization variable should be either "Length" or "Total_Punctuation".
	#This could probably be easily modified to allow any list of lists of lines, rather than just xml files.
	vals=[]
	for i in listofabsxmlfilepaths:
		vals.append(countenj(i,onlyfirstword)/(charcount(i[:-4]+".txt") if normalization=="Length" else countinlinepunc(i)))
	dict={}
	stdevs={}
	temp=[]
	for i in range(0,len(listofabsxmlfilepaths)):
		dict[listofabsxmlfilepaths[i].split("\\")[-1][:-4]]=vals[i]
	for i in dict.keys():
		temp.append(dict[i])
	stdev=np.array(temp).std()
	for i in dict.keys():
		stdevs[i]=stdev
	plotsinglebargraph(dict,"Document","Instances of Enjambment per Character",stdevs)
def main():
	texts=getsenecanames()
	parser=argparse.ArgumentParser()
	parser.add_argument("-count_sense_pauses",action="store_true")
	parser.add_argument("-only_within_line",action="store_false")
	parser.add_argument("-title",required=False)
	parser.add_argument("-onlyfirstword",required=False)
	parser.add_argument("-normalization",required=False)
	parser.add_argument("-output_format",default="Graph")
	args=parser.parse_args()
	if args.count_sense_pauses:
		to_test=[args.title] if args.title else texts	
		print to_test
		for i in to_test:
			print i+": "+str(countsensepauses(path_to_data+i+".txt",args.only_within_line))+" sense pauses"
	else:
		onlyfirstword=args.onlyfirstword=='True'
		normalization=args.normalization
		if args.normalization!="Length" and args.normalization!="Total_Punctuation":
			normalization="Length"
		absfilepaths=[os.path.abspath(path_to_data+i+".txt") for i in ([args.title] if args.title else texts)]
		plotmultiple(absfilepaths,onlyfirstword,normalization)
if __name__=="__main__":
	main()