from collections import defaultdict
import os
#import pylab
import re
#import matplotlib.pyplot as plt
import numpy as np
def list_directory_files(directory_index):
	return os.listdir(directory_index)
def getsenecanames():
	#List of the names of the seneca plays, without any file endings/paths
	return ["Agamemnon","HerculesFurens","Medea","Oedipus","Phaedra","Phoenissae","Thyestes","Troades","Octavia","HerculesOetaus"]
def getpathtoseneca():
	#Should return the path from the .py files to the Seneca texts. Change this line if the file organization is modified.
	return "../Data/SenecaTexts/"
def get_all_filepaths(path="",get_seneca_instead=False,exclude_choral_odes=False):
	#If get_seneca_instead is True, ignores path and fetches Seneca texts.
	if get_seneca_instead:
		path=getpathtoseneca()
		names=getsenecanames()
		appended_string="_without_choral_odes" if exclude_choral_odes else ""
		return [os.path.abspath(path+name+appended_string)+".txt" for name in names]
	return [os.path.abspath(path+i) for i in os.listdir(path)]
def getpathtochoralodes():
	return getpathtoseneca()+"choral_odes.txt"
def write_senecan_texts_without_choral_odes():
	#Duplicates the files for the Senecan plays, but exclues choral odes. The new version of Agamemnon.txt is Agamemnon_without_choral_odes.txt (and so on).
	#In theory this should never have to be run again after generating the files once, but nothing bad happens if it's rerun.
	texts=[]
	modified_texts=[]
	names=getsenecanames()
	for i in names:
		texts.append(getentirefile(os.path.abspath(getpathtoseneca()+i+".txt")))
	choral_odes=getentirefile(os.path.abspath(getpathtochoralodes())).split("\n")
	for text in texts:
		lines=text.split("\n")
		indices_to_remove=[]
		new_text=[]
		for line in lines:
			line_is_choral_ode=False
			for ode in choral_odes:
				if ode in line:
					line_is_choral_ode=True
					break
			if not line_is_choral_ode:
				new_text.append(line)
		modified_texts.append(new_text)
	for i in xrange(len(names)):
		f=open(getpathtoseneca()+names[i]+"_without_choral_odes.txt","w")
		for j in modified_texts[i]:
			f.write(j+"\n")
		f.close()
def getsenecanames_without_choral_odes():
	return [i+"_without_choral_odes" for i in getsenecanames()]
def getlivynames():
	#Same as getsenecanames(), but with Livy
	return ["Livy1","Livy21","Livy31","Livy39","Livy41"]
def getpathtolivy():
	#Same as getpathtoseneca(), but with Livy.
	return "../Data/LivyTexts/"
def getrelativepronouns():
	#List of relative pronouns.
	return ["qui","cuius","cui","quem","quo","quae","quam","qua","quod","quorum","quibus","quos","quarum","quas"]
def getentirefile(absfilepath):
	#Reads the entire file into one long string.
	return open(absfilepath,"r").read()
def parse(absfilepath,intochapters=False,intobooks=False):
	#Parses the file with path "absfilepath". If intochapters and intobooks are both false, returns a list of lines. If intochapters is true and intobooks is false, returns a list of
	#chapters, each of which is a list of lines. If intobooks is true, returns a list of books, each of which is a list of chapters, each of which is a list of lines.
	filetype=absfilepath[-3:]
	f=getentirefile(absfilepath)
	if filetype=="txt":
		return [i for i in f.split("\n") if i]
	elif filetype=="xml":
		lines=[]
		temp=f.split("<milestone")
		chapters=[]
		books=[[]]
		for longline in temp[1:]:
			line=longline[longline.index(">")+1:]
			if "chapter" in longline and (intochapters or intobooks):
				chapters.append([])
			if not line:
				continue
			for i in line:
				if i.isalpha():
					break
				if i=="<":
						line=line[line.index(">")+1:]
			# Remove tags such as <p>
			if "<" in line:
				line = re.sub('<[^>]*>', '', line).strip()
				#line=line[:line.index("<")]
			if len(line) != 0:
				# Remove abbreviated first names
				line = re.sub('([A-Z][A-Za-z]?[.])', '', line).replace('  ', ' ')
				if intochapters or intobooks:
					if chapters:
						chapters[-1].append(line)
						books[-1]=chapters
				else:
					lines.append(line)
			if "book" in longline and intobooks:
				books.append([])
				chapters=[]
		for i in range(0,len(books)):
			books[i]=[j for j in books[i] if j]
		return books if intobooks else chapters if intochapters else lines
	else:
		return []
def getlivypasses():
	#Parses the list of Livy suspected quotes from LivyPassages.csv. The csv file should probably be moved into the Data folder, in which case the file path in the first line below would need to be changed.
	f=getentirefile("LivyPassages.csv")
	lines=f.split("\n")
	for i in [j for j in lines if j]:
		if i[0]=="[":
			i=i[i.index("]")+1:]
	return [i[1:-1] for i in lines if i!="X" and i]
def charcount(absfilepath):
	#Counts the total number of characters of a play/book, given its file path. This function parses the file to avoid counting extraneous xml characters.
	count=0
	lines=parse(absfilepath)
	for line in lines:
		for char in line:
			if char.isalpha():
				count+=1
	return count
def plotsinglebargraph(dictofvalues,xlabel="X Axis Label",ylabel="Y Axis Label",stdevs=defaultdict(int),order=[],bin=1,show=True):
	#dictofvalues is a dictionary. Its keys are the values of the independent variable, and its values are the values of the dependent variable.
	#By default, the key for any given value will appear as a tick label on the x axis. To prevent this (e.g. if there are too many datapoints to read the labels), begin the key name with a backslash.
	#xlabel and ylabel are the labels that will appear on the x- and y-axes.
	#If provided, stdevs should be a dictionary with the same keys as dictofvalues. The standard deviation for each key should be the value of stdevs for that key.
	#If provided, order should be a list containing the same elements as dictofvalues.keys(), in the order that the values should appear on the plot. By default, the elements will appear in the order of dictofvalues.keys().
	#If there are many points, they can be binned using the "bin" value, which specifies the bin size.
	#A classics professor goes to a tailor to get his pants mended. The tailor asks: "Euripedes?" The professor replies "Yes. Eumenides?"
	#This has been color commentary. Back to code.
	maxval=0
	maxstdev=0
	orderedkeys=order if order else dictofvalues.keys()
	binneddict={}
	binnedorderedkeys=[]
	binnedstdevs={}
	for i in xrange(0,len(orderedkeys),bin):
		binnedorderedkeys.append(orderedkeys[i])
		for key in orderedkeys[i:i+bin]:
			if key[0]!="\\":
				binnedorderedkeys[-1]=key
		binneddict[binnedorderedkeys[-1]]=np.array([dictofvalues[j] for j in orderedkeys[i:i+bin]]).mean()
		binnedstdevs[binnedorderedkeys[-1]]=np.array([stdevs[j] for j in orderedkeys[i:i+bin]]).mean()
	orderedkeys=binnedorderedkeys
	stdevs=binnedstdevs
	vals=[binneddict[i] for i in orderedkeys]
	for i in orderedkeys:
		if dictofvalues[i]>maxval:
			maxval=dictofvalues[i]
		if stdevs[i]>maxstdev:
			maxstdev=stdevs[i]
	fig=plt.figure()
	ax=fig.add_subplot(111)
	ind=np.arange(len(orderedkeys))
	width=0.35
	stdevsexist=False
	for key in stdevs:
		if stdevs[key]:
			stdevsexist=True
	if stdevsexist:
		bar=ax.bar(ind,vals,width,color="red",yerr=[stdevs[i] for i in orderedkeys],edgecolor="none")
	else:
		bar=ax.bar(ind,vals,width,color="red",edgecolor="none")
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,maxval*1.05+maxstdev*1.05)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xticks(ind+width)
	xticknames=ax.set_xticklabels([("" if i[0]=="\\" else i) for i in orderedkeys])
	#If the dictionary index begins with a "\", it doesn't get displayed as a tick on the graph.
	plt.tight_layout(pad=0.4,w_pad=0.5,h_pad=1.0)
	plt.setp(xticknames,rotation=45,fontsize=10,ha="right")
	plt.gcf().subplots_adjust(bottom=0.15)
	plt.draw()
	if show:
		pylab.show()
def plothistogram(listofvalues,xlabel="X Axis Label",ylabel="Y Axis Label"):
	fig=plt.figure()
	ax=fig.add_subplot(111)
	width=1
	bars=[]
	top=0
	for i in range(0,len(listofvalues)):
		bars.append(ax.bar((i-0.5)*width,[listofvalues[i]],width,color="red"))
		if listofvalues[i]>top:
			top=listofvalues[i]
	ax.set_xlim(-width,len(listofvalues)+width)
	ax.set_ylim(0,top*1.05)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xticks([i*width*5 for i in range(0,len(listofvalues)/5)])
	xticknames=ax.set_xticklabels([str(i*5) for i in range(0,len(listofvalues)/5)])
	plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
	plt.setp(xticknames,rotation=45,fontsize=10,ha="center")
	plt.gcf().subplots_adjust(bottom=0.15)
	pylab.show()
def plotmultipletogether(listoflistsofvalues,listoflabels,xlabel="X Label",ylabel="Y Label",namesofbars=[]):
	fig=plt.figure()
	ax=fig.add_subplot(111)
	width=1
	bars=[]
	ind=np.arange(len(listoflabels))
	width=0.35
	for i in range(0,len(listoflabels)):
		bars.append(ax.bar(ind+i*width,listoflistsofvalues[i],width,color="red"))
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,max([max(i) for i in listoflistsofvalues])*1.05)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xticks(ind+len(listoflistsofvalues[0])*width)
	xticknames=["" if i[0]=="\\" else i for i in listoflabels]
	plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
	plt.setp(xticknames,rotation=45,fontsize=10)
	plt.gcf().subplots_adjust(bottom=0.15)
	if namesofbars:
		ax.legend((bars),(namesofbars))
def scatterplot(points,title="",xlabel="",ylabel="",hide_xticks=False,hide_yticks=False):
	#points is a a list of (x,y) duples.
	xvals,yvals=[i[0] for i in points],[i[1] for i in points]
	plt.plot(xvals,yvals,"r.")
	ax=plt.gca()
	if hide_xticks:
		plt.setp(ax.get_xticklabels(), visible=False)
	if hide_yticks:
		plt.setp(ax.get_yticklabels(), visible=False)
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.show()
	pass
# This is a pig. Pigs are completely unrelated to the project.
  ####                          _
  ####  _._ _..._ .-',     _.._(`))
  #### '-. `     '  /-._.-'    ',/
  ####    )         \            '.
  ####   / _    _    |             \
  ####  |  a    a    /              |
  ####  \   .-.                     ;  
  ####   '-('' ).-'       ,'       ;
  ####      '-;           |      .'
  ####         \           \    /
  ####         | 7  .__  _.-\   \
  ####         | |  |  ``/  /`  /
  ####        /,_|  |   /,_/   /
  ####           /,_/      '`-'
