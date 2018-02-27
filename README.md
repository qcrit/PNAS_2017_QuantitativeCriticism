# PNAS_2017_QuantitativeCriticism

The repository "PNAS_2017_QuantitativeCriticism" includes code relevant to the paper Dexter et al., "Quantitative criticism of literary relationships," PNAS (2017) 10.1073/pnas.1611910114.  

Use svmtests.py to run anomaly detection experiments on natural language texts. There are a number of dependencies, including scikit-learn. (N.B.: svmtests.py is incompatible with v. 0.19 of scikit-learn and any more recent versions. Prior to running the replication experiments described below, ensure that you have v. 0.18 installed.) The program takes optional arguments to define the bin size (in sentences), an additional text to analyze (other than Livy and the citation database), and whether to do leave-one-out cross-validation with books of Livy. For instance

python svmtests.py -b 35 -f "../Data/OtherTexts/Gal.txt" -l yes

would analyze Caesar's Bellum Gallicum as an additional text, with 35 sentence bins and leave-one-out cross-validation enabled. The default bin size is 35 bins. The features included can be modified by editing featuremethods = [] in svmtests.py, and the hyperparameters can be adjusted by changing the values of optimalgamma and optimalnu. For all experiments in the paper we set optimalgamma = 1/#features and optimalnu = 1/5. The raw data reported in Fig. 3B and C and in SI Appendix, Figs. S8 and S9 is provided in Livy_final_analysis.xlsx. 

features.py, sentences.py, punctuation.py, relativepronouns.py, functionalngrams.py, and usefulfunctions.py contain functions for computing the various stylometric features discussed in the paper (in both the Seneca and the Livy sections). Documentation is provided in the original files. general_caller.py can be used to obtain a quick count of a given feature in a particular text, as described therein. 

LivyPassages.csv contains the aggregated database of supsected Livian citations. Other relevant texts (such as Seneca, Livy, and Correr) can be found in the Data folder. The sub-folder OtherTexts contains the 17 Latin texts used in the comparative analysis reported in Fig. 3C.


