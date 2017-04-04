from __future__ import division
from functionalngrams import funcngrams
from punctuation import countenj,countinlinepunc,countsensepauses
from sentences import getlistofsentences,getlengthdistribution,avgsentencelength
from usefulfunctions import list_directory_files,getsenecanames,getpathtoseneca,getpathtochoralodes,getlivynames,getpathtolivy,parse,plotmultipletogether
import punctuation
import sentences
#The following is a simple way to calculate specific stylometric features.
def get_result(function,args):
	#"function" is a function object, and args is a list of arguments.
	return function(*args)
def main():
	#Here you can get (and manipulate) the results however you want, pretty much using regular Python.
	#You'll probably want to use one of the functions in the imports above.
	#Most of them should be documented to some degree in their respective files.
	#For example, to get the number of sentences in Agamemnon:
    
	func=getlistofsentences
	args=["./Data/SenecaTexts/Agamemnon.txt"]
	list_of_sentences=get_result(func,args)
	print len(list_of_sentences)

#To get a Python list of all files in a folder, use list_directory_files(folder_address).

if __name__=="__main__":
	main()