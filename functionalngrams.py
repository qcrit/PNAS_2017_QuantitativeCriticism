from __future__ import division
from collections import defaultdict
#from usefulfunctions import getsenecanames,getpathtoseneca,parse,getentirefile,charcount,plotsinglebargraph,plothistogram,scatterplot
import usefulfunctions as uf
import sys
import string
import operator
import pylab
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import re
path_to_data=uf.getpathtoseneca()
def funcngrams(absfilepath,ntemp,word_filter=[]):
	#Returns a dictionary of all n-grams in the provided text mapped to their frequencies.
	n=int(ntemp)
	d=defaultdict(int)
	lines=uf.parse(absfilepath)
	for line in lines:
		for text in line.split(" "):
			while not text[-1:].isalpha() and text:
				text=text[:-1]
			text=text.lower()
			if text in word_filter or not text:
				continue
			for i in range(0,(len(text))-n+1):
				d[text[i:i+n]]+=1
	return d
def ngram_line_distribution(lines,ngram):
	hits=[0 for line in lines]
	for line_index in xrange(len(lines)):
		if ngram in lines[line_index]:
			hits[line_index]=1
	return hits
def parsefiles(listoffilenames,n,word_filter=[]):
	#Synthesizes a larger dictionary given multiple files.
	listofdicts=[]
	parseddict=defaultdict(list)
	for i in listoffilenames:
		listofdicts.append(funcngrams(i,n,word_filter=word_filter))
	for i in listofdicts:
		for j in i.keys():
			parseddict[j].append(i[j])
	return parseddict
def plotvsavg(listoffilepaths,specificfilename="",n=2,numoftopchoices=5,word_filter=[],specfilepath=""):
	#Plots the most frequent n-grams in specificfilename and compares them to the frequency of those n-grams in listoffilepaths (which may or may not contain specificfilename).
	#Use specfilepath instead of specificfilename if the specific text is not a Seneca text.
	parsed=parsefiles(listoffilepaths,n,word_filter)
	if specificfilename=="all":
		this=parsed
	else:
		if not specfilepath:
			specfilepath=os.path.abspath(path_to_data+specificfilename)
		this=funcngrams(specfilepath,n,word_filter=word_filter)
	fig=plt.figure()
	ax=fig.add_subplot(111)
	topgrams=[]
	for i in reversed(sorted(this.iteritems(),key=operator.itemgetter(1))[-1*int(float(numoftopchoices)):]):
		topgrams.append(i[0])
	valuesforspecific=[]
	valuesforavg=[]
	stdevs=[]
	for i in topgrams:
		valuesforspecific.append(this[i])
		a=np.array(parsed[i])
		valuesforavg.append(a.sum())
		stdevs.append(a.std())
	ind=np.arange(numoftopchoices)
	count=0
	for i in listoffilepaths:
		count+=uf.charcount(i)
	for i in range(0,len(valuesforspecific)):
		valuesforspecific[i]/=uf.charcount(specfilepath)
	for i in range(0,len(valuesforavg)):
		valuesforavg[i]/=count
	top=max([max(valuesforspecific),max(valuesforavg)])+max(stdevs)/count*len(listoffilepaths)
	width=0.35
	specbar=ax.bar(ind,valuesforspecific,width,color="red")
	avgbar=ax.bar(ind+width,valuesforavg,width,color="blue",yerr=[i/count*len(listoffilepaths) for i in stdevs],ecolor="red")
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,top*1.05)
	ax.set_xlabel(str(n)+"-gram")
	ax.set_ylabel("Number of appearances per character")
	ax.set_xticks(ind+width)
	xticknames=ax.set_xticklabels(["\""+i+"\"" for i in topgrams])
	plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
	plt.setp(xticknames,rotation=45,fontsize=10)
	plt.gcf().subplots_adjust(bottom=0.15)
	ax.legend((specbar,avgbar),("\""+specificfilename[:-4]+"\"","Average"))
	plt.draw()
def plotallseneca(n,numtodisplay,includepseudoinmean=True,word_filter=[]):
	#Plots the frequency of the most frequent 100 n-grams in Seneca.
	#Not in use at the moment, -title all goes directly to plotvsavg.
	vals=parsefiles([path_to_data+i+".txt" for i in (getsenecanames() if includepseudoinmean else getsenecanames()[:-2])],n,word_filter=word_filter)
	sums=[]
	for i in vals.keys():
		sum=0
		for j in vals[i]:
			sum+=j
		sums.append([i,sum])
	f=open("seneca_"+str(n)+"grams.txt","w")
	for i in sorted(sums,key=operator.itemgetter(1))[::-1]:
		f.write("\""+i[0]+"\": "+str(i[1])+"\n")
	f.close()
	topgrams=[i[0] for i in reversed(sorted(vals.iteritems(),key=operator.itemgetter(1))[-1*int(numtodisplay):])]
	temp={}
	stdevs=[]
	for i in topgrams:
		temp[i]=vals[i]
		stdevs.append(np.array(temp[i]).std())
	print temp.keys()
	print [temp[i] for i in temp.keys()]
	plotsinglebargraph(temp,xlabel=str(n)+"-gram",ylabel="Number of appearances per character",stdevs=stdevs,order=topgrams)
def examine_specific_ngram(filepatharray,ngram):
	desired_word_frequencies=defaultdict(int)
	max_word_length=0
	for i in filepatharray:
		play=getentirefile(i)
		words=re.split(" |\n",play)
		for word in words:
			stripped_word=""
			for char in word:
				if char.isalpha():
					stripped_word+=char
			if ngram in word:
				desired_word_frequencies[stripped_word]+=1
				max_word_length=max(len(stripped_word),max_word_length)
	sorted_keys=sorted(desired_word_frequencies,key=lambda x:-desired_word_frequencies[x])
	for key in sorted_keys:
		print key+" "*(max_word_length-len(key))+"\t"+str(desired_word_frequencies[key])
def main():
	parser=argparse.ArgumentParser()
	#Only use -path when analyzing something outside of the directory with the Seneca code.
	parser.add_argument("-path",required=False)
	parser.add_argument("-title",required=False)
	parser.add_argument("-n",required=False,default=3)
	parser.add_argument("-numtodisplay",required=False,default=5)
	parser.add_argument("-word_filter",required=False,default="")
	parser.add_argument("-onlyseneca",required=False,default=False)
	parser.add_argument("-exclude_choral",required=False,default=False)
	parser.add_argument("-line_distribution",required=False)
	parser.add_argument("-examine_specific_ngram",required=False,default="")
	#examine_specific_ngram writes a list of (word containing n-gram,frequency of word) duples to stdout.
	args=parser.parse_args()
	if args.path[-1]!="/":
		args.path+="/"
	word_filter=args.word_filter.split(",")
	word_filter=[i.lower() for i in word_filter]
	temp_string_to_exclude_choral_verses="_without_choral_odes" if args.exclude_choral=="True" else ""
	if args.path:
		texts=uf.get_all_filepaths(path=args.path)+[path_to_data+i+temp_string_to_exclude_choral_verses+".txt" for i in uf.getsenecanames()]
	else:
		texts=uf.getsenecanames()
	#if args.onlyseneca=="True":	
	#	texts=texts[:-2]
	if args.path:
		textpaths=texts
	else:
		textpaths=[path_to_data+i+temp_string_to_exclude_choral_verses+".txt" for i in texts]
	numoftopchoices=int(args.numtodisplay)
	names_list=uf.getsenecanames() if args.title=="all" or not args.title else [args.path+args.title] if args.path else [args.title]
	if args.line_distribution:
		lines=uf.parse(path_to_data+args.title+temp_string_to_exclude_choral_verses+".txt")
		hits=ngram_line_distribution(lines,args.line_distribution)
		points=[(i,1) for i in xrange(len(hits)) if hits[i]==1]
		scatterplot(points,title="Distribution of \""+args.line_distribution+"\" in \""+args.title+"\" by line number (total of "+str(len(points))+"/"+str(len(lines))+" lines)", xlabel="Line Number",hide_yticks=True)
	elif args.examine_specific_ngram:
		examine_specific_ngram(textpaths,args.examine_specific_ngram)
	else:
		for name in names_list:
			plotvsavg(textpaths,name+temp_string_to_exclude_choral_verses+".txt",int(args.n),numoftopchoices,word_filter=word_filter,specfilepath=args.path+args.title if args.path else "")
	#plotvsavg([os.path.abspath(i) for i in textpaths],specificfilename,int(args.n),numoftopchoices,donotshow)
		pylab.show()
if __name__=="__main__":
	main()
