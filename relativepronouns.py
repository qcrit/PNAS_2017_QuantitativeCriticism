from __future__ import division
from sentences import getsentences
from usefulfunctions import getsenecanames,getpathtoseneca,getlivynames,getpathtolivy,getrelativepronouns,parse,plotsinglebargraph
import os
import argparse
import math
import numpy as np
def listofclauses(sentence):
	#Returns a list of relative clauses, given a sentence.
	if sentence[-1]=="?":
		return []
	clauses=[]
	words=sentence.split(" ")
	for i in range(0,len(words)):
		if words[i] in getrelativepronouns():
			temp=words[i]
			while i<len(words)-1 and words[i+1][-1:].isalpha():
				i+=1
				temp+=" "+words[i]
			clauses.append(temp[:-1])
	return clauses
def countsentenceswithrelativeclausesinlines(listoflines):
	#Counts the number of sentences with at least one relative clause in a list of lines
	count=0
	for s in getsentences(listoflines):
		if listofclauses(s):
			count+=1
	return count
def normnumofsentenceswithclauses(listoflines):
	return countsentenceswithrelativeclausesinlines(listoflines)/len(getsentences(listoflines))
def avgnumofclausespersentence(listoflines):
	#Returns the average number of relative clauses per sentence in a list of lines.
	nums=[]
	for sentence in getsentences(listoflines):
		l=listofclauses(sentence)
		#if l:
		nums.append(len(l))
	return np.array([i for i in nums if not math.isnan(i)]).mean()
def avgwordlengthofclauses(listoflines):
	#Returns the average word length of a relative clause in a give list of lines. Will return NaN if there are no relative clauses in the list of lines.
	lengths=[]
	for sentence in getsentences(listoflines):
		for clause in listofclauses(sentence):
			lengths.append(len(clause.split(" ")))
	return np.array([i for i in lengths if not math.isnan(i)]).mean()
def countsentenceswithrelativeclauses(absfilepath):
	return countsentenceswithrelativeclausesinlines(parse(absfilepath))
def plotnumofrelativeclauses(listoffilepaths):
	generalizedplotsetupfromlines([parse(i) for i in listoffilepaths],1,range(0,len(listoffilepaths)),markernames=getsenecanames(),header="Fraction of Sentences with a Relative Clause",dostdevs=True,bin=1)
	#Currently normalizes based on number of sentences.
def generalizedplotsetupfromlines(listoflistsoflines,option,placestoputmarkers=[],markernames=[],outputfilename="",header="",dostdevs=True,bin=10):
	#Generalized plot setup for displaying relative clause statistics.
	#option==1: Displays number of relative clauses in each list of lines, normalized
	#option==2: Displays the average number of clauses per sentence in each list of lines
	#option==3: Displays average word length of clauses in each list of lines
	#placestoputoutputmarkers is a list of indices in listoflistsoflines which should be marked on the x-axis.
	#If outputfilename is empty, the output does not get written to a file. Otherwise, writeoutputtofile is the title at the top of the data.
	dict={}
	stdevs={}
	keyorder=[]
	for i in range(0,len(listoflistsoflines)):
		key=str(markernames[len(keyorder)]) if i in placestoputmarkers else "\\"+str(i)
		keyorder.append(key)
		if option==1:
			dict[key]=countsentenceswithrelativeclausesinlines(listoflistsoflines[i])/len(getsentences(listoflistsoflines[i]))
		elif option==2:
			temp=[len(listofclauses(j)) for j in getsentences(listoflistsoflines[i])]
			arr=np.array([j for j in temp if j])
			dict[key]=arr.mean()
			if dostdevs:
				stdevs[key]=arr.std()
		elif option==3:
			lengths=[]
			for j in getsentences(listoflistsoflines[i]):
				lengths+=[len(k.split(" ")) for k in listofclauses(j)]
			dict[key]=np.array(lengths if lengths else [0]).mean()
	if dostdevs:
		stdev=np.array([dict[k] for k in keyorder]).std()
		for key in keyorder:
			stdevs[key]=stdev
	if outputfilename:
		output=header+"\n"
		currentbook=0
		for i in keyorder:
			if i[0]!="\\":
				currentbook+=11 if currentbook==10 else 1
				currentchapter=0
			currentchapter+=1
			output+="Chapter "+str(currentchapter-(1 if currentbook==1 else 0))+" of Livy book "+str(currentbook)+": "+str(dict[i])+"\n"
		f=open(outputfilename,"w")
		f.write(output)
		f.close()
	plotsinglebargraph(dict,"Text",header,order=keyorder,stdevs=stdevs if dostdevs else None,bin=bin)
def plotavgnumclausespersentence(listoffilepaths):
	#Use generalizedplotsetupfromlines instead of this function.
	vals={}
	stdevs={}
	for i in listoffilepaths:
		lengths=[len(listofclauses(sentence)) for sentence in getlistofsentences(i)]
		a=np.array([length for length in lengths if length])
		title=i.split("\\")[-1][:-4]
		vals[title]=a.mean()
		stdevs[title]=a.std()
	plotsinglebargraph(vals,"Text","Average # of relative clauses per sentence",stdevs)
def plotmeanlengthofclauses(listoffilepaths,byword=True):
	#Use generalizedplotsetupfromlines instead of this function.
	#Uses number of words if byword is True, uses character count if byword is false
	vals={}
	stdevs={}
	for absfilepath in listoffilepaths:
		title=absfilepath.split("\\")[-1][:-4]
		lengths=[]
		for i in getlistofsentences(absfilepath):
			for clause in listofclauses(i):
				lengths.append(len(clause.split(" ") if byword else clause))
		a=np.array(lengths)
		vals[title]=a.mean()
		stdevs[title]=a.std()
	plotsinglebargraph(vals,"Text","Average Length of Relative Clause",stdevs)
def main():
	listofsenecapaths=[os.path.abspath(getpathtoseneca()+i+".xml") for i in getsenecanames()]
	listoflivypaths=[os.path.abspath(getpathtolivy()+i+".xml") for i in getlivynames()]
	parser=argparse.ArgumentParser()
	parser.add_argument("-option",required=True)
	args=parser.parse_args()
	if args.option=="1":
		plotnumofrelativeclauses(listofsenecapaths)
	elif args.option=="2":
		plotavgnumclausespersentence(listofsenecapaths)
	elif args.option=="3":
		plotmeanlengthofclauses(listofsenecapaths)
	elif args.option=="4" or args.option=="5" or args.option=="6":
		listofchapters=[]
		placestoputmarkers=[]
		for i in range(0,len(listoflivypaths)):
			for j in parse(listoflivypaths[i],intobooks=True):
				placestoputmarkers.append(len(listofchapters))
				listofchapters+=[k for k in j]
		filename="Sentences_With_Clauses.txt" if args.option=="4" else "Clauses_Per_Sentence.txt" if args.option=="5" else "Length_Of_Clauses.txt"
		header="Fraction of sentences which have at least one relative clause" if args.option=="4" else "Average number of relative clauses per sentence" if args.option=="5" else "Average length of relative clauses"
		generalizedplotsetupfromlines(listofchapters,int(args.option)-3,placestoputmarkers,filename,header)
if __name__=="__main__":
	main()
