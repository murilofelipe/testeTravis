#!/usr/bin/python

import csv
import numpy as np
from sklearn.preprocessing import LabelBinarizer
import sys
from sklearn import tree
from datetime import datetime,date
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import train_test_split,StratifiedKFold
from sklearn.neighbors  import KNeighborsClassifier
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_score,recall_score,accuracy_score,f1_score,roc_auc_score,brier_score_loss
import matplotlib.pyplot as plt
from matplotlib import cm
from sklearn.datasets import make_blobs
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss



class Dataset:
    def __init__(self,name):
        self.name    = name
        self.dataset = None
        self.hheader = None
        self.vheader = None
        self.size = None
    def load(self):
        f = csv.reader(open(self.name),delimiter=',')
        t =[]
        hd = dict()
        hv = None
        novaDataSet = dict()
        count = -1
        for row in f:
            count +=1
            if hv == None:
                hv = []
                for j in range(len(row)):
                    hv.append(row[j])
                    hd[row[j]] = j
            else:
		row.append(0)
                t.append(row)
                
        self.dataset = np.matrix(t)
        self.header = hd
        self.vheader = hv
        self.onetarget = None
	self.size = count


    #Preenche o dataset utilizando os valores de latitude, longitude, e depois apontando para um atributo alvo
    def set_dataset_xy(self,dataset,alvo):
        self.datasetxy = self.dataset[:,dataset]
        self.target    = self.dataset[:,alvo]

    def convert_class(self):
        self.htarget = dict()
        self.chtarget = dict()
        for i in range(len(self.target)):
            value = self.target[i,0]
            if value not in self.htarget:
                self.htarget[value] = len(self.htarget)
                self.chtarget[value] = 1
            else:
                self.chtarget[value] +=1

        self.ttarget = []
        #print self.chtarget
        for i in range(len(self.target)):
               value = self.target[i,0]
               self.ttarget.append(self.htarget[value])

   
 
    
    def binarize_target(self):
        self.lb = LabelBinarizer()
        self.lb.fit(self.ttarget)
        self.mclass = self.lb.transform(self.ttarget)



    def set_class(self,att=1):
        if self.header == None:
            raise NameError('please load dataset first')
        attpos = att
        if type(att) == str:
            if att in self.header:
                attpos = self.header[att]
            else:
                raise NameError('%s not found in the loaded dataset'%(att))
        data = []
        head = []
        tail = []
        m = np.matrix(self.dataset)
        self.target = np.array([v for v in m[:,attpos].transpose().tolist()[0]])
        self.dataset = np.delete(m,np.s_[attpos],axis=1)




    #Funcao para corrigir data para datetime, preencher a coluna de feriado
    #Parametros: coluna data, coluna dia da semana
    def correct_date(self,data,weekday):
        m = np.matrix(self.dataset)
        
        dformat = '%Y-%m-%d %H:%M:%S'
        feriado =['01-01','01-18','02-14','02-15','03-16','04-03','05-05','05-08','05-30','06-19','07-04','09-05','10-10','10-30','11-11','11-24','11-24','11-25','12-25','12-31']
        weekend = ['Saturday','Sunday']
        # Preenche coluna de feriado para datas comemorativas e finais de semana
        for row in m:
            for i in range(len(row)):
                for j in feriado:
                    #print row
                    if row[i,data][5:10] == j :
                       row[i,-1] = 1
		       #print row
                for k in weekend:
                    if row[i,weekday] == k :
                       row[i,-1] = 1
		       #print row
        
        #Preenche a lista de data para sua forma datetime
        dates = [datetime.strptime(v,dformat).toordinal() for v in m[:,data].transpose().tolist()[0]]

        #Preenche no objeto dataset a data em seu formato datetime
        for j in range(len(dates)):
            self.dataset[j,data] = dates[j]
	    #self.datasetxy[j,data] = dates[j]
	    #print self.dataset[j,:]




    # Hold Out	
def holdOut(a,clf,ttarget):
	    X = a.datasetxy
	    y = ttarget
	    #print X
	    #print y
	    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3)
	    #Calibrar neighbors
            calibrar(a,clf,ttarget)
            #print "Score calibrado " + str(k)
	    #print "Tamanho total %d\nTamanho treino %d\nTamanho teste"%(len(X),len(X_train),len(X_test))
	
	    
	    clf.fit(X_train,y_train)
	    result = clf.predict(X_test)
	    #print result
	    mresult = confusion_matrix(y_test,result)
	    #print mresult
	    #print "precision %4.2f"%(precision_score(y_test,result))
	    #print "recall    %4.2f"%(recall_score(y_test,result))
	    #print "fl        %4.2f"%(f1_score(y_test,result))
	    #print "accuracy  %4.2f"%(accuracy_score(y_test,result))
	    tpos = np.sum(y_test)
	    tneg = len(y_test) - tpos
	    #print "total pos %d"%(tpos)
	    #print "total neg %d"%(tneg)
	    skf = StratifiedKFold(y,n_folds=10)
	    vprecision = []
	    vrecall = []
	    vfl = []
	    vaccuracy = []
	    
	    for train_index, test_index in skf:
	      #print train_index
	      #print test_index

	      X_train, X_test = X[train_index], X[test_index]
	      y_train, y_test = y[train_index], y[test_index]
	      
	      h= {'n_neighbors':range(1,50), 'metric':['euclidean', 'manhattan'], 'weights':['distance']}
	      
	      rscv = RandomizedSearchCV(clf,h,20) 
	      
	      rscv.fit(X_train,y_train)

	      result = rscv.predict(X_test)

	      mresult = confusion_matrix(y_test,result)
	      #print "Matriz de confusao do train"
	      #print mresult

	      #print "precision %4.2f"%(precision_score(y_test,result))
	      #print "recall    %4.2f"%(recall_score(y_test,result))
	      #print "f1        %4.2f"%(f1_score(y_test,result))
	      #print "accuracy  %4.2f"%(accuracy_score(y_test,result))
	      #print "--------------"
	      vprecision.append(precision_score(y_test,result))
	      vrecall.append(recall_score(y_test,result))
	      vfl.append(f1_score(y_test,result))
	      vaccuracy.append(accuracy_score(y_test,result))
	    print "precision %4.2f %4.2f"%(np.mean(vprecision), np.std(vprecision))
	    #print "recall    %4.2f %4.2f"%(np.mean(vrecall), np.std(vrecall))
	    #print "fl        %4.2f %4.2f"%(np.mean(vfl), np.std(vfl))
	    #print "accuracy  %4.2f %4.2f"%(np.mean(vaccuracy), np.std(vaccuracy))
	    #print "--------------"
	    print "vprecision: "
	    print vprecision
	    return vprecision

    #Funcao que passa por todas as classes
def OneForAll(a):
    	noCalibrado = dict()
    	vNo = []
	for classe in sorted(set(a.htarget)):
	    print "Classe " + classe
	    ttarget = a.mclass[:,a.htarget[classe]]

	    print "---------------------------"
		    
	    clf = KNeighborsClassifier(n_neighbors=50,weights='distance',metric='euclidean')
	    
	    # Treina e Testa com o mesmo conjunto (erro aparente)
	    clf.fit(a.datasetxy,ttarget)
	    result = clf.predict(a.datasetxy)
	    probi = clf.predict_proba(a.datasetxy)
	    mresult = confusion_matrix(ttarget,result)
	    # Hold Out 
	    #print self.holdOut(clf,ttarget)
	    holdOut(a,clf,ttarget)
	    print "Matriz de confusao"
	    print mresult
	    #print np.std(probi)
	    #print np.std(noCalibrado[classe])
	    #vNo.append(b.holdOut(clf,ttarget))
	#return vNo

	#imprimirCSV(b)	    
    		

    #Funcao que imprime em CSV
def imprimirCSV(a):
    fieldnames = []
    fieldnames.append("Id")
    print "Iniciando impressao"
    for classe in sorted(set(a.htarget)):
	fieldnames.append(classe)

    with open('testNovoTarget2.csv', 'wb') as csvfile:
    	#writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	#writer.writeheader()
	writer = csv.writer(csvfile, delimiter=',', quotechar='|')
	writer.writerow(fieldnames)
	for row in range(len(a.result)):
		#writer.writerow({fieldnames[0]:row})
		#str1 = str(row) + ","
		linha = []
		linha.append(row)
		for column in a.result[row]:
			#str2 = fieldnames[column+1] + str(a.result[row][column])
		    #str1 += str(column) + ","
		    linha.append(column)
		#print linha
		writer.writerow(linha)
		#writer.writerow({fieldnames[column+1]: a.result[row][column] for column in range(len(a.result[row]))})	 
    print "Impressao concluida"

def calibrar(a,clf,ttarget):
	X = a.datasetxy
	y = ttarget
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3)
	sig_clf = CalibratedClassifierCV(clf, method="sigmoid", cv="prefit")
	sig_clf.fit(X_train, y_train)
	clf_probs = sig_clf.predict_proba(X_test)
	score = log_loss(y_test, clf_probs)
	print "Score de log_loss: "+ str(score)

 
if __name__ == '__main__':
    a = Dataset(sys.argv[1])
    b = Dataset(sys.argv[2])
    a.load()
    b.load()
    
    
    
    a.correct_date(0,2)
    #dataset=[:,[X,Y]] target= category
    a.set_dataset_xy([-3,-2],1)
    #dataset=[:,[date,X,Y,feriado]] target= category
    #a.set_dataset_xy([0,-3,-2,-1],1)
    a.convert_class()
    a.binarize_target()
    #print a.datasetxy
    
    OneForAll(a)
    
    b.correct_date(1,2)
    #dataset=[:,[X,Y]] target= Id
    b.set_dataset_xy([-3,-2],0)
    #b.set_dataset_xy([1,-3,-2,-1],0) 
    b.convert_class()
    #b.binarize_target()
    
    
    #print b.datasetxy
    
    #k = OneForAll(a)
    #print ""
    #print k
    
    clf = KNeighborsClassifier(n_neighbors=50,weights='distance',metric='euclidean')
    
    # Treina e Testa com conjunto diferente
    clf.fit(a.datasetxy,a.target)
    a.result = clf.predict_proba(b.datasetxy)

    #print a.result   
	 #arquivo[classe] = result
	 #porID[row] = result
	    #a.probi = clf.predict_proba(b.datasetxy)
	 #print arquivo
    #print "Resolvendo..."
    imprimirCSV(a)
