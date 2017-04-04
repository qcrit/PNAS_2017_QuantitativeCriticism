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
	bin = 35
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
        
        
        # Full set of 25 features. The reduced set conists of the first 5 features listed.
		featuremethods=[normnumofsentenceswithclauses,avgnumofclausespersentence,getavgsentencelength,relative_clauses_per_sentence_average,sentence_length_variance,superlative_adjective_frequency,interrogative_sentence_frequency,conjunction_frequency,gerund_frequency,alius_frequency,atque_consonant_frequency,conjunction_cum_frequency,cond_cl_frequency,personal_pronoun_frequency,ipse_ngram_frequency,idem_ngram_frequency,indef_frequency,iste_ngram_frequency,ut_frequency,dum_frequency,priusquam_frequency,antequam_frequency,quin_frequency,third_person_pronoun_frequency, demonstrative_pronoun_frequency]


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
        
        # Set hyperparameters for one-class SVM. To replicate results in paper, set gamma = 1/#features and nu = 1/5.
		optimalgamma=1/25
		optimalnu=1/5
        
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
