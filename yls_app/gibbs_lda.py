# -*- coding: utf-8 -*-
# This file implements Author Topic LDA
# data sources
from yls_app.models import *
import numpy
import math
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
        ''' the following section is used for inference '''
        self.new_ndsum = {}
        self.new_nw = {}
        self.new_nd = {}
        self.new_nwsum = {}
        self.new_M = 0
        self.new_z = {}
        self.new_D = []
        ''' end new section '''
        self.z = {} # topic assignments for each word
        self.phisum = {}
        self.numstats = 0.0
        self.thetasum = {}
        self.run()

    def prepare_new_inference(self,docs_new,K,iterations):
        ''' load the neccesary z '''
        print 'WWWWWW',K
        results = read_results()
        print 'WWWWWWWW',results.keys()
        assert K in results.keys(),'The K %d not been calculated!'%(K,iterations)
        self.z = results[K]['z']
        self.new_M = len(docs_new)
        self.new_D = docs_new
        assert self.K == K
        ''' nd sum '''
        for i in range(self.new_M):
            self.new_ndsum[i] = 0.0
        ''' nw sum '''
        for j in range(self.K):
            self.nwsum[j] = 0.0
        ''' nw '''
        for i in range(self.V):
            self.new_nw[i] = {}
            for j in range(self.K):
                self.new_nw[i][j] = 0.0
        ''' nd '''
        for i in range(self.new_M):
            self.new_nd[i] = {}
            for j in range(self.K):
                self.new_nd[i][j] = 0.0
        ''' init all the old nds, nws '''
        for m in range(self.M):
            N = len(self.D[m])
            for n in range(N):
                topic = self.z[m][n]
                self.nw[self.D[m][n]][topic] = self.nw[self.D[m][n]].get(topic, 0) + 1
                self.nd[m][topic] = self.nd[m].get(topic, 0) + 1
                self.nwsum[topic] = self.nwsum.get(topic, 0) + 1
            self.ndsum[m] = N

        ''' init all the new nds, nws '''
        for m in range(self.new_M):
            N = len(self.new_D[m]) 
            self.new_z[m] = []
            for n in range(N):
                topic = int(random.random() * self.K)
                self.new_z[m].append(topic)
                self.new_nw[self.new_D[m][n]][topic] = self.new_nw[self.new_D[m][n]].get(topic, 0) + 1
                self.new_nd[m][topic] = self.new_nd[m].get(topic, 0) + 1
                self.new_nwsum[topic] = self.new_nwsum.get(topic, 0) + 1
            self.new_ndsum[m] = N
            
    def gibbs_inferecne(self,alpha, beta, infer_iteration):
        self.alpha = alpha
        self.beta = beta

        for i in range(self.maxIter):
            print "in inference iteration", i , time.ctime()
            for m in range(len(self.new_z)):
                for n in range(len(self.new_z[m])):
                    self.new_z[m][n] = self.sample_full_conditional_infer(m, n)

    def sample_full_conditional_infer(self, m, n):
        topic = self.new_z[m][n]
        w = self.new_D[m][n]
        
        self.new_nw[w][topic] -= 1
        self.new_nd[m][topic] -= 1
        self.new_nwsum[topic] -= 1
        self.new_ndsum[m] -= 1

        p = {}
        for k in range(self.K):
            p[k] = (self.new_nw[w][k] + self.nw[w][k] + self.beta) / (self.nwsum[k] + self.new_nwsum[k] + self.V * self.beta) * (self.new_nd[m][k] + self.alpha) / (self.new_ndsum[m] + self.K * self.alpha)
        
        for k in range(1, len(p)): p[k] += p[k - 1]
        u = random.random() * p[self.K - 1]
        for topic in range(len(p)):
            if u < p[topic]: break

        self.new_nw[w][topic] += 1  
        self.new_nd[m][topic] += 1  
        self.new_nwsum[topic] += 1
        self.new_ndsum[m] += 1

        return topic



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
        t = Task.create_new_lda_task()
        t.status = Task.TASK_STATUS_STARTED
        t.save()

        for i in range(self.maxIter):
            print "iteration", i , time.ctime()
            t.info = "iteration" + str(i) + " " + str(time.ctime())
            t.save()
            for m in range(len(self.z)):
                for n in range(len(self.z[m])):
                    self.z[m][n] = self.sample_full_conditional(m, n)

            if i % 100 == 0:
                self.update_params()
        Task.finish_task(t,success=True)

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

    def get_new_theta(self):
        theta = {}
        for m in range(self.new_M):
            theta[m] = {}
            for k in range(self.K):
                theta[m][k] = 0

        for m in range(self.new_M):
            for k in range(self.K):
                theta[m][k] = (self.new_nd[m][k] + self.alpha) / (self.new_ndsum[m] + self.K * self.alpha); 

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
    iterations = 500
    K = 30
    documents = []
    for entry in TweetUserToken.objects.all()[0:50]:
#    for entry in TweetToken.objects.all()[0:10000]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        if len(this_doct) > 1500:
            random.shuffle(this_doct)
            this_doct = this_doct[0:1500]

        documents.append(this_doct)
    fommm = map(len,documents)
    fommm.sort()
    #print fommm[0], fommm[-1]

    print 'Documents readed %d'%(len(documents))
    for K in [30]:
        lda = LdaGibbsSampler(documents, K, len(V))
        lda.configure(iterations,2000,20)
        lda.gibbs(alpha,beta)
        theta = lda.get_theta()
        # theta is in the format of 
        # {docid: {topic0: prob, topic1:prob}}
    
        phi = lda.get_phi()
        # phi is in the formate of
        # {topicid: {word0:prob, ... , word0:}}
        save_to_file(K,iterations,phi,theta,lda.z)
        # calculate the most hot topic
        hot_topic = [0] *K
        for doc in phi.keys():
            topic_dist = [phi[doc][k] for k in phi[doc].keys()]
            hot_topic = [hot_topic[i] + topic_dist[i] for i in range(len(hot_topic))]
        hot_topic = [float(k)/sum(hot_topic) for k in hot_topic]
        hot_topic = zip(range(K),hot_topic)
        hot_topic.sort(key=lambda k:k[1],reverse=True)
        print 'HOTTOPICS------------------'
        for topic in hot_topic:
            print topic[0], topic[1]

def save_to_file(K,iterations,phi,theta,z):
    ''' results = {(K,iterations):{phi,theta,z}} } '''
    if os.path.exists('yls_app/gibbs_results'):
        f = open('yls_app/gibbs_results','r')
        results = pickle.load(f)
        f.close()
    else:
        results = {}

    if K not in results.keys():
        results[K] = {}
    results[K]['phi'] = phi
    results[K]['theta'] = theta
    results[K]['z'] = z

    f = open('yls_app/gibbs_results','w')
    pickle.dump(results,f)
    f.close()

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

def read_results():
    f = open('yls_app/gibbs_results','r')
    results = pickle.load(f)
    f.close()
    return results

def cal_perplexity(meaningful_words_path,phi_file_name,theta_file_name,K):
    perplexity = {}
    for K in [100, 70, 40, 10, 110, 80, 50, 20, 90, 60, 30]:
        perplexity[K] = cal_perplexity_inner(meaningful_words_path,phi_file_name,theta_file_name,K)
    for ww in perplexity.keys():
        print 'Topic %d, perplexity %f',ww,perplexity[ww]
    return perplexity

def cal_perplexity_inner(meaningful_words_path,phi_file_name,theta_file_name,K):
    ''' use the 100-110 to test the model '''
    alpha = 2.0
    beta = 0.5
    N_TEST = 10
    TEST_START = 100

    V = run_lda.read_vocab(meaningful_words_path)
    Vset = set(V)
    documents = []
    for entry in TweetUserToken.objects.all()[0:50]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        if len(this_doct) > 1500:
            random.shuffle(this_doct)
            this_doct = this_doct[0:1500]
        assert all(map(lambda k:k != -1,this_doct))
        documents.append(this_doct)
    new_documents = []
    for entry in TweetUserToken.objects.all()[TEST_START:TEST_START+N_TEST]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        new_documents.append(this_doct)

    def do_inference(iterations):
        lda = LdaGibbsSampler(documents,K,len(V))
        lda.configure(iterations,2000,20)
        lda.prepare_new_inference(new_documents,K,iterations)
        lda.gibbs_inferecne(alpha,beta,iterations)
        return lda.get_new_theta()

    new_theta = do_inference(100)
    phi = read_results()[K]['phi']

    def p(w,d):
        ''' p(w) = sigma_z P(z,w) = sigma_z P(z) * p(w|z)
        w is the index of V '''
        return sum([new_theta[d][z] * phi[z][w] for z in range(K)])

    p_final = 1.0
    for i in range(len(new_documents)):
        doc = new_documents[i]
#    for doc in documents:
        for a_word in doc:
            p_a_word = p(a_word,i)
            p_final *= (1.0/p_a_word)**(1.0/sum(map(len,new_documents)) )

    print 'perplexity ',p_final
    print read_results().keys()
    return p_final

# inference the goods's topic distribution
def read_goods_group_topic_results():
    if os.path.exists('yls_app/goods_results') == False:
        return {}
    f = open('yls_app/goods_results','r')
    results = pickle.load(f)
    f.close()
    return results

def save_goods_group_topic_results(result):
    f = open('yls_app/goods_results','w')
    pickle.dump(result,f)
    f.close()

def read_single_good_topic_results():
    if os.path.exists('yls_app/the_good_results') == False:
        return {}
    f = open('yls_app/the_good_results','r')
    results = pickle.load(f)
    f.close()
    return results

def save_single_good_topic_results(result):
    f = open('yls_app/the_good_results','w')
    pickle.dump(result,f)
    f.close()


# the wrapper for calculating how much goods category recommended
def goods_recommend(func):
    def new_Func(*args, **args2):
        count = 0
        goods = {}
        f = open('yls_app/goods_hit_results','r')
        goods = pickle.load(f)
        f.close()

        for i in WeiboUser.objects.all()[220:]:
            print '==============%d==========='%(count)
            count += 1
            try:
                results = func(args[0],i.name)
            except Exception:
                continue
            for mm in results[1:]:
                goods[mm[0]] += 1

            f = open('yls_app/goods_hit_results','w')
            pickle.dump(goods,f)
            f.close()

        assert False
        return []
    return new_Func

#@goods_recommend    
def recommend(meaningful_words_path,user,alpha=2,beta=0.5):
    # generate the file formats needed by the LDA sampler
    print 'start runing lda gibbs....'
    V = run_lda.read_vocab(meaningful_words_path)
    Vset = set(V)
    iterations = 50
    K = 40
    new_documents = []
    documents = []
    results = read_goods_group_topic_results()
    save_the_results = False
    load_from_results = True

    # read the tweets of this user
    for entry in TweetUserToken.objects.filter(user_name=user):
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        new_documents.append(this_doct)
    new_documents = [new_documents[0]]

    # read old data
    for entry in TweetUserToken.objects.all()[0:50]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        if len(this_doct) > 1500:
            random.shuffle(this_doct)
            this_doct = this_doct[0:1500]
        assert all(map(lambda k:k != -1,this_doct))
        documents.append(this_doct)
 
    def do_inference(iterations,new):
        lda = LdaGibbsSampler(documents,K,len(V))
        lda.configure(iterations,2000,20)
        lda.prepare_new_inference(new,K,iterations)
        lda.gibbs_inferecne(alpha,beta,iterations)
        return lda.get_new_theta()

    goods_html = []
    for entry in GoodsProcessedGroup.objects.all().iterator():
        tokens = filter(lambda k:k in Vset, entry.product_des.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        if len(tokens) > 15:
            new_documents.append(this_doct)
            #print this_doct
            goods_html.append(entry.category_name)

    if load_from_results == False:
        new_theta_goods = do_inference(2000,new_documents)
        new_theta_goods = [new_theta_goods[k] for k in new_theta_goods.keys()]
        new_theta_goods = [[m[k] for k in m.keys()] for m in new_theta_goods]
        new_theta = new_theta_goods[0]
        new_theta_goods = new_theta_goods[1:]
    else:
        the_results = read_goods_group_topic_results()
        new_documents = [new_documents[0]]
        new_theta = do_inference(100,new_documents)
        new_theta = [new_theta[k] for k in new_theta.keys()]
        new_theta = [[m[k] for k in m.keys()] for m in new_theta]
        new_theta_goods = [(k,the_results[k]) for k in the_results.keys()]
        #print new_theta_goods
        new_theta = new_theta[0]
    
    if save_the_results == True:
        for i in range(len(goods_html)):
            results[goods_html[i]] = new_theta_goods[i]
        #print results
        save_goods_group_topic_results(results)

    if load_from_results == False:
        assert len(new_theta_goods) == len(goods_html)
        new_theta_goods = zip(goods_html,new_theta_goods)

    def cos(a,b):
        #print b[0]
        #print len(a),len(b)
        assert len(a) == len(b)
        amb = sum([a[k]*b[k] for k in range(len(a))])
        a_mod = sum([a[k]**2 for k in range(len(a))])**0.5
        b_mod = sum([b[k]**2 for k in range(len(b))])**0.5
        #print amb/(a_mod*b_mod)
        return amb/(a_mod*b_mod)

    def KL(a,b):
        assert len(a) == len(b)
        Dab = 0.5*sum([a[i]*math.log(a[i]/float(b[i]),2) for i in range(len(a))])
        Dba = 0.5*sum([b[i]*math.log(b[i]/float(a[i]),2) for i in range(len(b))])
#        return Dab + Dba
        return sum([(a[i]-b[i])**2 for i in range(len(a))])

    def cal_distance(that):
        #print that
        return cos(new_theta,that)

    def cal_distance_KL(that):
        return KL(new_theta,that)

    results = sorted(new_theta_goods, key=lambda k:cal_distance(k[1]),reverse=True)
    results_KL = sorted(new_theta_goods,key=lambda k:cal_distance_KL(k[1]))

    print ' for review only ===================='
    temp_original = []
    temp_KL = []
    for i in results[0:15]:
        if i[0] not in [m[0] for m in results_KL[0:15]]:
            temp_original.append(i[0])

    for i in results_KL[0:15]:
        if i[0] not in [m[0] for m in results[0:15]]:
            temp_KL.append(i[0])

    print 'original..........'
    for i in temp_original:
        print i
    print 'KL...............'
    for i in temp_KL:
        print i
    print ' review finishes ===================='

    print 'Choosable', len(new_documents)
    for m in results[0:15]:
        print m[0], abs(cos(new_theta,m[1]))
    # {user:new_theta, goods:[[m[1], cos]]}
    ret_results = []
    ret_results.append(new_theta)
    count = 1
    for m in results[0:15]:
        ret_results.append([m[0],m[1],'goods_%d.png'%(count),cos(new_theta,m[1])])
        count += 1
    
    return ret_results

def recommend_the_good_save_results(meaningful_words_path,user,cats_goods,weights_goods,alpha=2,beta=0.5):
    # generate the file formats needed by the LDA sampler
    print 'start runing lda gibbs....'
    V = run_lda.read_vocab(meaningful_words_path)
    Vset = set(V)
    iterations = 50
    K = 40
    new_documents = []
    documents = []
    results = read_single_good_topic_results()
    new_documents = []
    save_results = True

    # read the tweets of this user
    for entry in TweetUserToken.objects.filter(user_name=user):
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        new_documents.append(this_doct)
    new_documents = [new_documents[0]]

    # read old data
    for entry in TweetUserToken.objects.all()[0:50]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        if len(this_doct) > 1500:
            random.shuffle(this_doct)
            this_doct = this_doct[0:1500]
        assert all(map(lambda k:k != -1,this_doct))
        documents.append(this_doct)
 
    def do_inference(iterations,new):
        lda = LdaGibbsSampler(documents,K,len(V))
        lda.configure(iterations,2000,20)
        lda.prepare_new_inference(new,K,iterations)
        lda.gibbs_inferecne(alpha,beta,iterations)
        return lda.get_new_theta()

    goods_html = []
    for entry in GoodsProcessed.objects.all().iterator():
        tokens = filter(lambda k:k in Vset, entry.product_des.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        if len(tokens) > 3:
            new_documents.append(this_doct)
            #print this_doct
            goods_html.append((entry.product_html,entry.product_category))

    if save_results == True:
        new_theta_goods = do_inference(2000,new_documents)
        new_theta_goods = [new_theta_goods[k] for k in new_theta_goods.keys()]
        new_theta_goods = [[m[k] for k in m.keys()] for m in new_theta_goods]
        new_theta = new_theta_goods[0]
        new_theta_goods = new_theta_goods[1:]
        for i in range(len(goods_html)):
            results[goods_html[i]] = new_theta_goods[i]
        save_single_good_topic_results(results)
        new_theta_goods = zip(goods_html,new_theta_goods)
    else:
        the_results = read_single_good_topic_results()
        new_documents = [new_documents[0]]
        new_theta = do_inference(100,new_documents)
        new_theta = [new_theta[k] for k in new_theta.keys()]
        new_theta = [[m[k] for k in m.keys()] for m in new_theta]
        new_theta_goods = [(k,the_results[k]) for k in the_results.keys()]
        #print new_theta_goods
        new_theta = new_theta[0]

    def KL(a,b):
        assert len(a) == len(b)
        Dab = 0.5*sum([a[i]*math.log(a[i]/float(b[i]),2) for i in range(len(a))])
        Dba = 0.5*sum([b[i]*math.log(b[i]/float(a[i]),2) for i in range(len(b))])
#        return Dab + Dba
        return sum([(a[i]-b[i])**2 for i in range(len(a))])

    def cal_distance_KL(that):
        return KL(new_theta,that)
    #print new_theta_goods
    results = sorted(new_theta_goods,key=lambda k:cal_distance_KL(k[1]))
#ret_results = {'cats':[product_html,product_html]}
    ret_results = {}
    for cat_to_rec,weight_to_rec in zip(cats_goods,weights_goods):
        the_res = [m for m in results if m[0][1] == cat_to_rec]
        the_res = the_res[0:weight_to_rec]
        ret_results[cat_to_rec] = the_res
    
    print 'Choosable', len(new_documents)
    for m in results[0:15]:
        print m[0], abs(KL(new_theta,m[1]))
    # {user:new_theta, goods:[[m[1], cos]]}
    to_ret = []
    for k in ret_results.keys():
        temp = ret_results[k]
        for tt in temp:
            to_ret.append(tt[0][0])
    print '-------------'
    for mm in to_ret:
        print mm
    return to_ret

def goods_rec(meaningful_words_path,user,number_goods = 20):
    results = recommend(meaningful_words_path,user)
    results = results[1:]
    weighteds = [m[3] for m in results]
    numbers = [float(number_goods)*weighteds[i]/sum(weighteds) for i in range(len(weighteds))]
    numbers = [int(i+1) for i in numbers]
    ret = []

    categories = [results[i][0] for i in range(len(numbers))]

    assert len(categories) == len(numbers)

    ret = recommend_the_good_save_results(meaningful_words_path,user,categories,numbers)

    print ret
    return ret
    

# random recommend
def goods_rec_random(meaningful_words_path,user,number_goods = 20):
    results = recommend(meaningful_words_path,user)
    results = results[1:]
    weighteds = [m[3] for m in results]
    numbers = [float(number_goods)*weighteds[i]/sum(weighteds) for i in range(len(weighteds))]
    numbers = [int(i+1) for i in numbers]
#    print 'Numbers',numbers
    def choose_from_category(cat,numbers):
        w = []
#        print 'Cat',cat
        assert numbers > 0
        for m in GoodsProcessed.objects.filter(product_category=cat):
            w.append(m.product_html)
        random.shuffle(w)
        return w[0:numbers]
        
    ret = []
    for i in range(len(numbers)):
#        print results[i],'---'
        for i in choose_from_category(results[i][0],numbers[i]):
            ret.append(i)
    print ret
    return ret
        
        
    
