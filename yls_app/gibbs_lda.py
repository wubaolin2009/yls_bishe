# -*- coding: utf-8 -*-
# This file implements Author Topic LDA
# data sources
from yls_app.models import *
import numpy
import random
import os
import run_lda
import bisect
import time
import pickle

#this file implments the LDA algorithm by Gibss Sampling
# Not an online algo

class LdaGibbsSampler:
    def __init__(self, Data, K, V):
        self.D = Data # Data to be inputed
        self.K = K
        self.V = V
        self.M = len(self.D)
        self.alpha = 2
        self.beta = 0.5
        self.maxIter = 1000
        self.burnIn = 100
        self.sampleLag = 20
        self.ndsum = {} # total number of words in document i
        self.nw = {} # number of instances of word i (term?) assigned to topic j
        self.nd = {} # number of words in document i assigned to topic j
        self.nwsum = {} # total number of words assigned to topic j
        self.z = {} # topic assignments for each word
        self.phisum = {}
        self.numstats = 0.0
        self.thetasum = {}
        self.run()

    def run(self):
        self.set_ND()\
            .set_NW()\
            .set_NWSUM()\
            .set_NDSUM()

    def set_NDSUM(self):
        for i in range(self.M):
            self.ndsum[i] = 0.0
        return self

    def set_NWSUM(self):
        for j in range(self.K):
            self.nwsum[j] = 0.0
        return self

    def set_NW(self):
        for i in range(self.V):
            self.nw[i] = {}
            for j in range(self.K):
                self.nw[i][j] = 0.0
        return self

    def set_ND(self):
        for i in range(self.M):
            self.nd[i] = {}
            for j in range(self.K):
                self.nd[i][j] = 0.0
        return self

    def set_M(self, value = 0):
        self.M = value
        return self

    def set_V(self):
        Set = set()
        for s in self.D:
            Set = Set | set(s)
        self.V = len(Set)
        print "self.V =", self.V
        return self

    def set_K(self, value):
        self.K = value
        return self

    def set_alpha(self, value):
        self.alpha = value
        return self

    def set_beta(self, value):
        self.beta = value
        return self

    def configure(self, iterations, burnIn, sampleLag):
        self.maxIter = iterations
        self.burnIn = burnIn
        self.sampleLag = sampleLag

    def set_thetasum(self):
        for m in range(self.M):
            self.thetasum[m] = {}
            for j in range(self.K):
                self.thetasum[m][j] = 0.0
        return self

    def set_phisum(self):
        for k in range(self.K):
            self.phisum[k] = {}
            for v in range(self.V):
                self.phisum[k][v] = 0.0
        return self

    def gibbs(self, alpha = 2, beta = 0.5):
        self.alpha = alpha
        self.beta = beta
        if self.sampleLag > 0:
            self.set_thetasum()\
                .set_phisum()
            self.numstats = 0.0
        self.initial_state()
        for i in range(self.maxIter):
            print "iteration", i , time.ctime()
            for m in range(len(self.z)):
                for n in range(len(self.z[m])):
                    self.z[m][n] = self.sample_full_conditional(m, n)

#            if i > self.burnIn and self.sampleLag > 0 and i % self.sampleLag == 0:
            self.update_params()

    def sample_full_conditional(self, m, n):
        topic = self.z[m][n]
        
        self.nw[self.D[m][n]][topic] -= 1
        self.nd[m][topic] -= 1
        self.nwsum[topic] -= 1
        self.ndsum[m] -= 1
        
        p = {}
        for k in range(self.K):
            p[k] = (self.nw[self.D[m][n]][k] + self.beta) / (self.nwsum[k] + self.V * self.beta) * (self.nd[m][k] + self.alpha) / (self.ndsum[m] + self.K * self.alpha)
        
        for k in range(1, len(p)): p[k] += p[k - 1]
        u = random.random() * p[self.K - 1]
        for topic in range(len(p)):
            if u < p[topic]: break
        self.nw[self.D[m][n]][topic] += 1  
        self.nd[m][topic] += 1  
        self.nwsum[topic] += 1
        self.ndsum[m] += 1
        return topic

    def update_params(self):
        for m in range(len(self.D)):
            for k in range(self.K):
                self.thetasum[m][k] += (self.nd[m][k] + self.alpha) / (self.ndsum[m] + self.K * self.alpha)
        for k in range(self.K):
            for w in range(self.V):
                self.phisum[k][w] += (self.nw[w][k] + self.beta) / (self.nwsum[k] + self.V * self.beta)
        self.numstats += 1

    def initial_state(self):
        for m in range(self.M):
            N = len(self.D[m]) 
            self.z[m] = []
            for n in range(N):
                topic = int(random.random() * self.K)
                self.z[m].append(topic)
                self.nw[self.D[m][n]][topic] = self.nw[self.D[m][n]].get(topic, 0) + 1
                
                self.nd[m][topic] = self.nd[m].get(topic, 0) + 1

                self.nwsum[topic] = self.nwsum.get(topic, 0) + 1
                
                n += 1
            self.ndsum[m] = N
            
            m += 1

    def get_theta(self):
        theta = {}
        for m in range(self.M):
            theta[m] = {}
            for k in range(self.K):
                theta[m][k] = 0
        if self.sampleLag > 0:
            for m in range(self.M):
                for k in range(self.K):
                    print self.thetasum[m][k], self.numstats
                    theta[m][k] = self.thetasum[m][k] / self.numstats
        else:
            for m in range(self.M):
                for k in range(self.K):
                    theta[m][k] = (self.nd[m][k] + self.alpha) / (self.ndsum[m] + self.K * self.alpha); 
        return theta

    def get_phi(self):
        phi = {}
        for k in range(self.K):
            phi[k] = {}
            for v in range(self.V):
                phi[k][v] = 0
        if self.sampleLag > 0:
            for k in range(self.K):
                for v in range(self.V):
                    phi[k][v] = self.phisum[k][v] / self.numstats
        else:
            for k in range(self.K):
                for v in range(self.V):
                    phi[k][v] = (self.nw[k][v] + self.alpha) / (self.nwsum[k] + self.K * self.alpha); 
        return phi

def run_lda_gibbs(meaningful_words_path,K, iterations,alpha=2,beta=0.5):
    # generate the file formats needed by the LDA sampler
    print 'start runing lda gibbs....'
    V = run_lda.read_vocab(meaningful_words_path)
    Vset = set(V)
    iterations = 1

    documents = []
    for entry in TweetUserToken.objects.all()[0:500]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        documents.append(this_doct)

    print 'Documents readed %d'%(len(documents))
    
    lda = LdaGibbsSampler(documents, K, len(V))
    lda.configure(iterations,2000,20)
    lda.gibbs(alpha,beta)
    theta = lda.get_theta()
    # theta is in the format of 
    # {docid: {topic0: prob, topic1:prob}}

    phi = lda.get_phi()
    # phi is in the formate of
    # {topicid: {word0:prob, ... , word0:}}

    # save using pickle
    f = open('yls_app/phi','w')
    pickle.dump(phi,f)
    f.close()

    f = open('yls_app/theta','w')
    pickle.dump(theta,f)
    f.close()
    
    #print the topic distribution
#    for topic in range(10):
#        print 'Topic %d'%(topic)
#        words = phi[topic]
#        words = [(i,words[i]) for i in words.keys()]
#        words.sort(key=lambda a:a[1], reverse=True)
#        for a_word in words[0:10]:
#            print V[a_word[0]],'::',a_word[1]


def get_results(vocab_file, topic_numbers, word_in_topic):
    ret = dict()
    ret['success'] = 1
    ret['message'] = 'success'
    ret['topics'] = []
    # randomly choose one type of panel
    panel_types = ('panel-primary','panel-success','panel-info','panel-warning','panel-danger')
    # save the new result?
    save_new_result = (Topic.objects.all().count() == 0)
    if not save_new_result:
        for topic in Topic.objects.all():
            this_topic = []
            topic_color = panel_types[random.randint(0,len(panel_types)-1)]
            for topic_word in TopicWord.objects.filter(topic=topic):
                this_topic.append([topic_word.topic.topic_id, topic_word.word, topic_word.freq, topic_color, topic.topic_name])
            ret['topics'].append(this_topic)
        return ret

    vocab = run_lda.read_vocab(vocab_file)

    f = open('yls_app/phi','r')
    phi = pickle.load(f)
    f.close()

    f = open('yls_app/theta','r')
    theta = pickle.load(f)
    f.close()

    for k in range(0, topic_numbers):
        this_topic = []
        print 'topic %d:' % (k)
        t = Topic(topic_id=k, topic_name=u'未分类')
        t.save()

        topic_color = panel_types[random.randint(0,len(panel_types)-1)]
        phi_this_topic = [(i,phi[k][i]) for i in phi[k].keys()]
        phi_this_topic.sort(reverse=True,key=lambda k:k[1])
        for i in range(0, word_in_topic):
            word,freq = phi_this_topic[i]
            TopicWord(topic=t, word=vocab[word], freq = "%.10f"%freq).save()
            this_topic.append([k, vocab[word], "%.6f"%freq, topic_color, u'未分类']) # add color
        ret['topics'].append(this_topic)

    return ret
