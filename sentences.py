from collections import defaultdict
from usefulfunctions import getsenecanames,getpathtoseneca,getlivynames,getpathtolivy,parse,plotsinglebargraph,plothistogram
import argparse
import os
import numpy as np
from pprint import pprint

def getlistofsentences(absfilepath):	
	return getsentences(parse(absfilepath))

def getsentences(lines):
	#Gets a list of sentences given a list of lines. The original line breaks are discarded.
	sentences=[]
	temp=""
	for line in lines:
		for char in line:
			temp+=char
			# Last condition in the if doesn't let a sentence end with a one (capital) letter word and then a period.
			# This is to prevent against abbrev first names in Livy splitting sentences
			if (char in [".","?","!"] and len(temp)>=3
				and temp[-3].isalpha()
				and not (temp[-3] == ' ' and temp[-2].upper() == temp[-2] and temp[-1] == '.')):
				sentences.append(temp)
				temp=""
	return sentences if sentences else lines

def getavgsentencelength(lines):
	return np.array([len(i.split(" ")) for i in getsentences(lines)]).mean()

def getlengthdistribution(absfilepaths):
	#Gets the distribution of sentence length for a list of file paths. For example, if [0,4,7] is returned, the input files have 0 sentences of length 0, 4 sentences of length 1, and 7 of length 2.
	numofeachlength=defaultdict(int)
	maxlength=0
	for path in absfilepaths:
		for s in getlistofsentences(path):
			if len(s.split(" "))>maxlength:
				maxlength=len(s.split(" "))
			numofeachlength[len(s.split(" "))]+=1
		listofvals=[]
	for i in range(0,maxlength+1):
		listofvals.append(numofeachlength[i])
	return listofvals

def avgsentencelength(absfilepath):
	return np.array([len(i) for i in getlistofsentences(absfilepath)]).mean()

def main():
	paths=[os.path.abspath(getpathtolivy()+i+".xml") for i in getlivynames()]
	parser=argparse.ArgumentParser()
	parser.add_argument("-author",required=True)
	parser.add_argument("-by",required=False)
	args=parser.parse_args()

	#texts=getsenecanames()
	#dict={}
	#for i in texts:
	#	dict[i]=avgsentencelength(os.path.abspath(getpathtoseneca()+i+".xml"))
	#plotsinglebargraph(dict,"Text","Average Sentence Length")
	#f=open("livysentencelength.txt","w")
	#books=[]
	#for i in paths:
	#	books+=parse(i,intobooks=True)
	#for i in range(0,len(books)):
	#	val=i+1 if i<10 else i+11
	#	for j in range(0,len(books[i])):
	#		f.write("Chapter "+str(i+1)+" of Book "+str(val)+": "+str(np.array(len(getsentences(books[i][j]))).mean())+"\n")
	#f.close()
	plothistogram(getlengthdistribution([os.path.abspath((getpathtolivy() if args.author=="livy" else getpathtoseneca())+i+".xml") for i in (getlivynames() if args.author=="livy" else getsenecanames())])[:50],"Sentence Length","Number of Sentences")

if __name__=="__main__":
	main()
