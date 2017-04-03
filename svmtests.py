from __future__ import division
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from random import shuffle
from usefulfunctions import getsenecanames,getpathtoseneca,getlivynames,getpathtolivy,parse,getlivypasses
from relativepronouns import normnumofsentenceswithclauses,avgnumofclausespersentence,avgwordlengthofclauses
from punctuation import countenjambments,countinlinepuncfromlines
from sentences import getavgsentencelength,getsentences
from features import relative_clauses_per_sentence_average,sentence_length_variance,superlative_adjective_frequency,interrogative_sentence_frequency,conjunction_frequency,gerund_frequency,alius_frequency,neque_aut_ratio,neque_nec_ratio,atque_consonant_frequency,conjunction_cum_frequency,cond_cl_frequency,personal_pronoun_frequency,ipse_ngram_frequency,idem_ngram_frequency,indef_frequency,iste_ngram_frequency,ut_frequency,quominus_frequency,dum_frequency,priusquam_frequency,antequam_frequency,quin_frequency,third_person_pronoun_frequency, demonstrative_pronoun_frequency
import copy
import math
import numpy as np
import sys
import re
import argparse
import warnings


def getnormedfeaturesforlines(featuremethods,listofmeans,listofstdevs,listoflines):
	#Computes and normalizes a feature list for a given list of lines
	return [(featuremethods[i](listoflines)-listofmeans[i])/listofstdevs[i] for i in range(0,len(featuremethods))]

def train(featuremethods,trainingdata,classification="anomaly_detection",gamma=0,nu=0.5,features=None):
	#trainingdata is a list of [listoflines,value] duples. For anomaly detection, value is always 0.
	if not features:
		features=[]
		for bunchoflines in trainingdata:
			features.append([i(bunchoflines) for i in featuremethods])
	means=[np.array([i[j] for i in features]).mean() for j in range(0,len(featuremethods))]
	stdevs=[np.array([i[j] for i in features]).std() for j in range(0,len(featuremethods))]
	tempfeatures=copy.deepcopy(features)
	for bunchoflines in tempfeatures:
		for feature in range(0,len(bunchoflines)):
			bunchoflines[feature]-=means[feature]
			bunchoflines[feature]/=stdevs[feature]
	parameters={'gamma':[0,10],'nu':[0.1,0.9]}
	if classification=="anomaly_detection":
		svr=svm.OneClassSVM(kernel='rbf',degree=3,coef0=0.0,tol=0.001,shrinking=True,cache_size=200,verbose=False,max_iter=-1,random_state=None,gamma=gamma,nu=nu)
	elif classification=="elliptic_envelope":
		svr=EllipticEnvelope()
	else:
		svr=svm.SVC(cache_size=200,class_weight=None,coef0=0.0,kernel="rbf",max_iter=-1,probability=False,random_state=None,shrinking=True,tol=0.001,verbose=False)
	if classification=="anomaly_detection":
		svr.fit(tempfeatures)
	elif classification=="elliptic_envelope":
		return [svr.decision_function(tempfeatures),means,stdevs]
	else:
		svr.fit(tempfeatures,[1 for i in trainingdata])
	return [svr,means,stdevs]

def dogridsearch(traininglines,featuremethods):
	#Gridsearches for gamma and nu given the training lines and feature methods.
	gridsearch=[]
	features=[]
	max=0
	for bunchoflines in traininglines:
		features.append([i(bunchoflines) for i in featuremethods])
	for gamma in xrange(0,10):
		gridsearch.append([])
		print gamma
		for nu in xrange(1,10):
			gridsearch[gamma].append([])
			temp=train(featuremethods,[[i,0] for i in traininglines],gamma=gamma,nu=nu/10,features=features)
			inputs=[getnormedfeaturesforlines(featuremethods,temp[1],temp[2],text) for text in traininglines]
			count=0
			for i in inputs:
				gridsearch[gamma][nu-1].append(temp[0].predict(i))
				if gridsearch[gamma][nu-1][-1]==1:
					count+=1
			if count>max:
				max=count
				vals=[gamma,nu/10]
	return vals

'''def old_main():
	"""INPUT ARGUMENTS: -b 15 -f filename.txt
	-b lets you specify the number of quotes per bin
	-f filename lets you specify the filename for lines of text placed in an another text file."""
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', type=int, help='number of sentences per bin')
	parser.add_argument('-f', type=str, help='filename for other quotes to test.')
	args = parser.parse_args()
	
	# Set defaults if parameters not chosen
	bin = 15
	if args.b:
		bin = args.b

	othertestlines = []
	num_other_test_lines = 0
	# Check if we want to use our own quotes to test
	if args.f:
		othertestlines = open(args.f, 'r').readlines()
		num_other_test_lines = len(othertestlines)
	
	optimalgamma=0
	optimalnu=0.1
	senecalines=[parse(getpathtoseneca()+book+".txt",intobooks=True) for book in getsenecanames()]
	templivylines=[parse(getpathtolivy()+book+".xml",intobooks=True) for book in getlivynames()]
	livylines=[]

	for i in templivylines:
		livylines+=i
	for i in xrange(len(livylines)):
		l=[]
		for chap in livylines[i]:
			l+=chap
		livylines[i]=l
	livylines=livylines[:10]+livylines[11:]
	
	avglenofquote=np.array([len(i) for i in livylines]).mean()
	#traininglines=senecalines[:8]
	featuremethods=[normnumofsentenceswithclauses,avgnumofclausespersentence,getavgsentencelength]

	# Uncomment the two lines below to gridsearch for gamma and nu values, then change the values of
	# optimalgamma and optimalnu at the top. For Livy, the gridsearch takes several minutes, so it's
	# best not to run it every time.
	#print dogridsearch(traininglines,featuremethods)
	#return

	traininglines=[parse(getpathtolivy()+book+".xml") for book in getlivynames()]
	traininglines = ''.join(traininglines).split('.')

	#Feature methods should accept a list of lines, and return a single number.
	#senecavals=[1 for i in range(0,8)]+[-1 for i in range(8,10)]
	testing='blah' #testing="quotes"
	classtype="anomaly_detection"
	livypasses=getlivypasses()
	count=0
	totalcount=0

	for oddout in xrange(0,1 if testing=="quotes" else (len(livylines))):
		print str(oddout) + " EXCLUDED:"
		traininglines=livylines[:oddout]+livylines[oddout+1:]
		features=[]
		for bunchoflines in traininglines:
			if bunchoflines:
				features.append([i(bunchoflines) for i in featuremethods])
		temp=train(featuremethods,[[i,0] for i in traininglines],classification=classtype,gamma=optimalgamma,nu=optimalnu,features=features)
		leninoddout=int(bin*avglenofquote/np.array([len(j) for j in livylines[oddout]]).mean())
		new=livypasses if testing=="quotes" else livylines[oddout]
		new.extend(othertestlines)
		for i in xrange(0,len(new),(bin if testing=="quotes" else leninoddout)):
			catted=[]
			for j in range(i,i+bin):
				if j>=len(new):
					break
				catted+=new[j]
			normed=getnormedfeaturesforlines(featuremethods,temp[1],temp[2],catted if testing=="quotes" else livylines[oddout][i:i+leninoddout])
			val=temp[0](normed) if classtype=="elliptic_envelope" else temp[0].predict(normed)
			if val[0]==1.:
				count+=1
			totalcount+=1
			print str(normed)+" "+str(val)
	print count
	print totalcount
	print "NOTE: The results from the text file are the last " + str(int(num_other_test_lines / bin)) + " lines of the output."
	return count'''











def main():
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
	"""Example input arguments -b 15 -f filename.txt -l yes."""
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', type=int, help='number of sentences per bin')
	parser.add_argument('-f', type=str, help='filename for other quotes to test.')
	parser.add_argument('-l', type=str, help='give "yes" for leave one out analysis, "no" otherwise')
	args = parser.parse_args()
		
	# Set defaults if parameters not chosen
	bin = 15
	if args.b:
		bin = args.b

	# Check if we want to use our own quotes to test
	otherlines_temp = []
	othertestlines = []
	if args.f:
		otherlines_temp = open(args.f, 'r').readlines()
		for i in xrange(len(otherlines_temp)):
			otherlines_temp[i] = re.sub('([A-Z][A-Za-z]?[.])', '', otherlines_temp[i]).replace('  ', ' ')
		otherlines_temp = [line + '.' for line in ''.join(otherlines_temp).replace('\n', ' ').replace('  ', ' ').split('.')]
		othertestlines = []
		for i in xrange(int(len(otherlines_temp) / bin)): # Split into bins
			othertestlines.append(''.join(otherlines_temp[i * bin:(i + 1) * bin]))

	# Check if we're leaving one book out or not
	loo = True
	if args.l:
		if args.l.lower() == 'no' or args.l.lower() == 'false':
			loo = False

	# Collect lines
	senecalines=[parse(getpathtoseneca()+book+".txt",intobooks=True) for book in getsenecanames()]
	templivylines=[parse(getpathtolivy()+book+".xml",intobooks=True) for book in getlivynames()]	

	livylines=[]
	for i in templivylines:
		livylines+=i
	for i in xrange(len(livylines)):
		l=[]
		for chap in livylines[i]:
			l+=chap
		livylines[i]=l
	livylines=livylines[:10]+livylines[11:]

	for left_out_book in xrange(len(livylines)):
		print
		print "Left out book: ", left_out_book + 1
		traininglines_temp = []
		for i in xrange(len(livylines)):
			if i != left_out_book:
				traininglines_temp.extend(livylines[i])
		traininglines_temp = [line.strip() + '.' for line in ''.join(traininglines_temp).replace('\n', ' ').replace('  ', ' ').split('.')]

		#print "num sentences", len(traininglines_temp), l
		traininglines = []
		for i in xrange(int(len(traininglines_temp) / bin)): # Split into bins
			traininglines.append(''.join(traininglines_temp[i * bin:(i + 1) * bin]))

		# Test lines for left out book
		livy_lo_lines_temp = [line.strip() + '.' for line in ''.join(livylines[left_out_book]).replace('\n', ' ').replace('  ', ' ').split('.')]
		livy_lo_lines = []
		for i in xrange(int(len(livy_lo_lines_temp) / bin)): # Split into bins
			livy_lo_lines.append(''.join(livy_lo_lines_temp[i * bin:(i + 1) * bin]))

		featuremethods=[normnumofsentenceswithclauses,avgnumofclausespersentence,getavgsentencelength,relative_clauses_per_sentence_average,sentence_length_variance]

#featuremethods=[normnumofsentenceswithclauses,avgnumofclausespersentence,getavgsentencelength,relative_clauses_per_sentence_average,sentence_length_variance,superlative_adjective_frequency,interrogative_sentence_frequency,conjunction_frequency,gerund_frequency,alius_frequency,atque_consonant_frequency,conjunction_cum_frequency,cond_cl_frequency,personal_pronoun_frequency,ipse_ngram_frequency,idem_ngram_frequency,indef_frequency,iste_ngram_frequency,ut_frequency,dum_frequency,priusquam_frequency,antequam_frequency,quin_frequency,third_person_pronoun_frequency, demonstrative_pronoun_frequency]
#featuremethods=[normnumofsentenceswithclauses,avgnumofclausespersentence,getavgsentencelength]
#,superlative_adjective_frequency,interrogative_sentence_frequency,conjunction_frequency,gerund_frequency,alius_frequency,neque_aut_ratio,neque_nec_ratio,atque_consonant_frequency,conjunction_cum_frequency,cond_cl_frequency,personal_pronoun_frequency,ipse_ngram_frequency,idem_ngram_frequency,indef_frequency,iste_ngram_frequency,ut_frequency,quominus_frequency,dum_frequency,priusquam_frequency,antequam_frequency,quin_frequency
		# Uncomment the two lines below to gridsearch for gamma and nu values, then change the values of
		# optimalgamma and optimalnu at the top. For Livy, the gridsearch takes several minutes, so it's	
		# best not to run it every time.
        #print dogridsearch(traininglines,featuremethods)
        #return

		testing="quotes"
		classtype="anomaly_detection"
		livypasses_temp = getlivypasses()
		livypasses_temp = [line + '.' for line in ''.join(livypasses_temp).replace('\n', ' ').replace('  ', ' ').split('.')]
		livypasses = []
		for i in xrange(int(len(livypasses_temp) / bin)): # Split into bins
			livypasses.append(''.join(livypasses_temp[i * bin:(i + 1) * bin]))

		livy_book_count = 0
		livy_book_totalcount = 0
		livy_quote_count=0
		livy_quote_totalcount=0
		other_quote_count=0
		other_quote_totalcount=0
		optimalgamma=1/5
		optimalnu=0.2
		features=[]
		for bunchoflines in traininglines:
			if bunchoflines:
				features.append([i(bunchoflines) for i in featuremethods])
		temp=train(featuremethods,
				   [[i,0] for i in traininglines],
				   classification=classtype,
				   gamma=optimalgamma,
				   nu=optimalnu,
				   features=features)

		new=copy.copy(livypasses)
		new.extend(othertestlines)

		#for i in xrange(len(traininglines)):
		#	normed=getnormedfeaturesforlines(featuremethods, temp[1], temp[2], traininglines[i])
		#	val=temp[0](normed) if classtype=="elliptic_envelope" else temp[0].predict(normed)
		#	#print "Livy training set: ", str(normed) + " " + str(val)
		#	if val[0]==1.:
		#		livy_book_count += 1
		#	livy_book_totalcount += 1

		for i in xrange(len(livy_lo_lines)):
			normed=getnormedfeaturesforlines(featuremethods, temp[1], temp[2], livy_lo_lines[i])
			val=temp[0](normed) if classtype=="elliptic_envelope" else temp[0].predict(normed)
			#print "Livy training set: ", str(normed) + " " + str(val)
			if val[0]>0.5:
				livy_book_count += 1
			livy_book_totalcount += 1

		for i in xrange(len(new)):
			normed=getnormedfeaturesforlines(featuremethods, temp[1], temp[2], new[i])
			val=temp[0](normed) if classtype=="elliptic_envelope" else temp[0].predict(normed)
			if i < len(livypasses):
				#print "Livy quote database: ", str(normed) + " " + str(val)
				if val[0]>0.5:
					livy_quote_count += 1
				livy_quote_totalcount += 1
			else:
				#print "User .txt file quote bin: ", str(normed) + " " + str(val)
				if val[0]>0.5:
					other_quote_count += 1
				other_quote_totalcount += 1
	
		print "Number of livy book quotes (binned) classified as Livy: ", livy_book_count
		print "Total number of livy book quotes (binned): ", livy_book_totalcount
		print "Number of livy database quotes (binned) classified as Livy: ", livy_quote_count
		print "Total number of livy quotes (binned): ", livy_quote_totalcount
		print "Number of .txt quotes (binned) classified as Livy: ", other_quote_count
		print "Total number of .txt quotes (binned): ", other_quote_totalcount











if __name__=="__main__":
	#old_main()
	main()
