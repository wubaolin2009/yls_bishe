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
# parameters for AT-LDA
K = 30
alpha = 50.0/K
beta = 0.01
#alpha = 2.0
#beta = 0.5
# Author Number
Author_number = 50
iterations_to_train = 500
# where the test set begins and ends
TEST_BEGIN = 100
TEST_NUMBER = 10
TEST_END = TEST_BEGIN + TEST_NUMBER
infer_iterations = 10

def cal_na(nak,a):
    return sum(nak[a])

def cal_nk(nkw,k):
    return sum(nkw[k])

def save_results(K,Kmn,Amn,phi,theta,nak,nkw,na,nk):
    if os.path.exists('yls_app/at_results') == False:
        f = open('yls_app/at_results','w')
        pickle.dump({},f)
        f.close()
    f = open('yls_app/at_results','r')
    results = pickle.load(f)
    to_save = {'Kmn':Kmn, 'Amn':Amn,'phi':phi,'theta':theta,
               'nak':nak, 'nkw':nkw,'na':na,'nk':nk}
    f.close()
    f = open('yls_app/at_results','w')
    results[K] = to_save    
    pickle.dump(results,f)
    f.close()

def get_results():
    f = open('yls_app/at_results','r')
    results = pickle.load(f)
    f.close()
    return results

def at_lda():
    for K in [30]:
        print 'KKKKKKKKKKKKKKKKKKKKKKK',K
        at_lda_inner(K)
    calculate_perplexity()

def at_lda_inner(K):
    all_author_token = []
    # get the vocabulary file
    V = run_lda.read_vocab('yls_app/tools/wbl_80_converted_manual_processed')
    Vset = set(V)

    # Read all authors and their tokens
    print 'load all the tokens'
    for entry in TweetUserToken.objects.all()[0:Author_number]:
        author = entry.user_name
        tokens = entry.tokens
        tokens = filter(lambda k:k in Vset, tokens.split(u' '))
        if len(tokens) > 400:
            random.shuffle(tokens)
            tokens = tokens[0:400]
        tokens = map(V.index,tokens)

        all_author_token.append((author,tokens))

    all_authors = [m[0] for m in all_author_token]

    # store tha topic
    Kmn = []
    # store the author
    Amn = []
    for m in all_author_token:
        author,tokens = m
        Kmn.append([-1 for i in range(len(tokens))])
        Amn.append([-1 for i in range(len(tokens))])

    print 'Tokens number are %d'%(sum(map(len,Kmn)))
        
    #Init All K and A randomly
    for m in range(len(Kmn)):
        for n in range(len(Kmn[m])):
            Kmn[m][n] = random.randint(0,K-1)
            Amn[m][n] = random.randint(0,len(all_authors)-1)

    nak = [[0 for m in range(K)] for i in range(len(all_authors))]
    nkw = [[0 for w in range(len(V))] for i in range(K)]

    for m in range(len(Kmn)):
        for n in range(len(Kmn[m])):
            k,a = Kmn[m][n],Amn[m][n]
            nak[a][k] += 1
            w = all_author_token[m][1][n]
            nkw[k][w] += 1

    na = [cal_na(nak,a) for a in range(len(all_authors))]
    nk = [cal_nk(nkw,k) for k in range(K)]

    def exeTime(func):  
        def newFunc(*args, **args2):  
            t0 = time.time()  
            print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)  
            back = func(*args, **args2)  
            print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)  
            print "@%.5fs taken for {%s}" % (time.time() - t0, func.__name__)  
            return back  
        return newFunc

    def sample_k_a(w):
        LENA = len(all_authors)
        p = [0] * (LENA*K)
        for k in range(K):
            pre = (nkw[k][w] + beta)/float(nk[k]+len(V)*beta)
            for a in range(LENA):
                index = k*LENA + a
                p[index] = (nak[a][k]+alpha)/(na[a]+K*alpha) * pre
                assert nkw[k][w] >= 0
                assert nk[k] >= 0
                assert nak[a][k] >= 0
                assert na[a] >= 0

        weighted_sum = [0 for _ in range(K*LENA+1)]
        weighted_sum[0] = p[0]
        for i in range(1,len(p)):
            weighted_sum[i] = weighted_sum[i-1] + p[index]
        weighted_sum[len(p)] = weighted_sum[len(p)-1]

        selected_index = -1
        target = random.random() * weighted_sum[len(p)]
        selected_index = bisect.bisect_right(weighted_sum,target)
        if selected_index == len(weighted_sum) - 1:
            selected_index -= 1

        assert selected_index != -1

        return (selected_index / LENA, selected_index % LENA)

    iterations = iterations_to_train
    for iteration in range(0,iterations):
        print 'iteration %d'%(iteration),time.ctime()
        for m in range(len(Kmn)):
            #print 'processing doc %d tokens %d'%(m,len(all_author_token[m][1]))
            for w_index in range(len(Kmn[m])):
                #w = bisect.bisect_right(V,all_author_token[m][1][w_index]) - 1
                w = all_author_token[m][1][w_index]
                k,a = Kmn[m][w_index],Amn[m][w_index]
                nak[a][k],na[a],nkw[k][w],nk[k] = nak[a][k]-1,na[a]-1,nkw[k][w]-1,nk[k]-1
                assert nkw[k][w] >= 0
                assert nk[k] >= 0
                assert nak[a][k] >= 0
                assert na[a] >= 0

                #sample new topic k, and author a
                new_k,new_a = sample_k_a(w)
                #new_k,new_a = 1,1
                Kmn[m][w_index] = new_k
                Amn[m][w_index] = new_a
                #update nak, na, nkw,nk
                nak[new_a][new_k],na[new_a],nkw[new_k][w],nk[new_k] = nak[new_a][new_k]+1,na[new_a]+1,nkw[new_k][w]+1,nk[new_k]+1

        #cal sita
        sita = [[0 for _ in range(K)] for _ in range(len(all_authors))]
        for a in range(len(all_authors)):
            for k in range(K):
                sita[a][k] = (nak[a][k] + alpha) / (K * alpha + na[a])
        
        #cal phi
        phi = [[0 for _ in range(len(V))] for _ in range(K)]
        for k in range(K):
            for t in range(len(V)):
                phi[k][t] = (nkw[k][t] + beta) / (len(V)*beta + nk[k])

        save_results(K,Kmn,Amn,phi,sita,nak,nkw,na,nk)

def at_lda_inference(TEST_K):
    K = TEST_K
    all_author_token = []

    # get the vocabulary file
    V = run_lda.read_vocab('yls_app/tools/wbl_80_converted_manual_processed')
    Vset = set(V)

    # Read all authors and their tokens
    print 'load all the tokens'
    for entry in TweetUserToken.objects.all()[TEST_BEGIN:TEST_END]:
        author = entry.user_name
        tokens = entry.tokens
        tokens = filter(lambda k:k in Vset, tokens.split(u' '))
        tokens = map(V.index,tokens)
        all_author_token.append((author,tokens))

    # store tha topic
    Kmn = []
    # store the author
    Amn = []
    print get_results().keys()
    results = get_results()[TEST_K]
    Kmn = results['Kmn']
    Amn = results['Amn']
    phi = results['phi']
    theta = results['theta']

    #Init All new_K and new_A randomly
    # store tha topic
    new_Kmn = []
    # store the author
    new_Amn = []
    for m in all_author_token:
        author,tokens = m
        new_Kmn.append([-1 for i in range(len(tokens))])
        new_Amn.append([-1 for i in range(len(tokens))])

    for m in range(len(new_Kmn)):
        for n in range(len(new_Kmn[m])):
            new_Kmn[m][n] = random.randint(0,K-1)
            new_Amn[m][n] = random.randint(0,Author_number - 1)

    nak = results['nak']
    nkw = results['nkw']
    na = results['na']
    nk = results['nk']
    
    assert len(all_author_token) == TEST_NUMBER

    new_nak = [[0 for m in range(K)] for i in range(Author_number)]
    new_nkw = [[0 for w in range(len(V))] for i in range(K)]
    # init new_nak and new_nkw
    for m in range(len(new_Kmn)):
        for n in range(len(new_Kmn[m])):
            k,a = new_Kmn[m][n],new_Amn[m][n]
            new_nak[a][k] += 1
            w = all_author_token[m][1][n]
            new_nkw[k][w] += 1
    
    new_na = [sum(nak[a]) for a in range(Author_number)]
    new_nk = [sum(nkw[k]) for k in range(K)]

    def sample_k_a_infer(w):
        LENA = len(all_author_token)
        p = [0] * (LENA*K)
        for k in range(K):
            pre = (new_nkw[k][w] + nkw[k][w] + beta)/float(new_nk[k] + nk[k]+len(V)*beta)
            for a in range(LENA):
                index = k*LENA + a
                #print (new_na[a]),K*alpha
                p[index] = (new_nak[a][k] + nak[a][k]+alpha)/(new_na[a] + na[a]+K*alpha) * pre
                #p[index]=1
        weighted_sum = [0 for _ in range(K*LENA+1)]
        weighted_sum[0] = p[0]
        for i in range(1,len(p)):
            weighted_sum[i] = weighted_sum[i-1] + p[index]
        weighted_sum[len(p)] = weighted_sum[len(p)-1]

        selected_index = -1
        target = random.random() * weighted_sum[len(p)]
        selected_index = bisect.bisect_right(weighted_sum,target)
        assert selected_index != -1
        return (selected_index / LENA, selected_index % LENA)

    iterations = infer_iterations
    for iteration in range(0,iterations):
        print 'iteration infering... %d'%(iteration),time.ctime()
        for m in range(len(new_Kmn)):
            for w_index in range(len(new_Kmn[m])):
                w = all_author_token[m][1][w_index]
                k,a = new_Kmn[m][w_index],new_Amn[m][w_index]
                new_nak[a][k],new_na[a],new_nkw[k][w],new_nk[k] = new_nak[a][k]-1,new_na[a]-1,new_nkw[k][w]-1,new_nk[k]-1
                #sample new topic k, and author a
                new_k,new_a = sample_k_a_infer(w)
                #new_k,new_a = 1,1
                new_Kmn[m][w_index] = new_k
                new_Amn[m][w_index] = new_a
                #update nak, na, nkw,nk
#                print '0',new_nak[new_a][new_k]
#                print '1',new_na[new_a]
#                print '2',new_nkw[new_k][w]
                new_nak[new_a][new_k],new_na[new_a],new_nkw[new_k][w],new_nk[new_k] = new_nak[new_a][new_k]+1,new_na[new_a]+1,new_nkw[new_k][w]+1,new_nk[new_k]+1

    #cal sita
    sita = [[0 for _ in range(K)] for _ in range(Author_number)]
    for a in range(Author_number):
        for k in range(K):
            sita[a][k] = (new_nak[a][k] + alpha) / (K * alpha + new_na[a])
        
    #cal phi
    phi = [[0 for _ in range(len(V))] for _ in range(K)]
    for k in range(K):
        for t in range(len(V)):
            phi[k][t] = (new_nkw[k][t] + beta) / (len(V)*beta + new_nk[k])
    return sita,phi,new_Amn

def calculate_perplexity():
    perp = {}
    for TEST_K in [10,20,30,40,50,60,70,80,90,100,110]:
        perp_value = calculate_perplexity_inner(TEST_K)
        perp[TEST_K] = perp_value
    for k in perp.keys():
        print "K %d,value %f"%(k,perp[k])

def calculate_perplexity_inner(TEST_K):
    sita,phi,Amn = at_lda_inference(TEST_K)
    new_documents = []
    K = TEST_K

    V = run_lda.read_vocab('yls_app/tools/wbl_80_converted_manual_processed')
    Vset = set(V)

    for entry in TweetUserToken.objects.all()[TEST_BEGIN:TEST_END]:
        tokens = filter(lambda k:k in Vset, entry.tokens.split(u' '))
        this_doct = map(lambda k:V.index(k), tokens)
        assert all(map(lambda k:k != -1,this_doct))
        new_documents.append(this_doct)

    new_theta = sita

    def p(documents,i,j):
        ''' p(w) = sigma_z P(z,w) = sigma_z P(z) * p(w|z)
        w is the index of V '''
        w = documents[i][j]
#        print i,j,len(Amn)
        a = Amn[i][j]
        return sum([new_theta[a][z] * phi[z][w] for z in range(K)])
#       return sum([new_theta[i][z] * phi[z][w] for z in range(K)])

    p_final = 1.0
    for i in range(len(new_documents)):
        doc = new_documents[i]
#    for doc in documents:
        for j in range(len(doc)):
#        for a_word in doc:
            a_word = doc[j]
            p_a_word = p(new_documents,i,j)
            p_final *= (1.0/p_a_word)**(1.0/sum(map(len,new_documents)) )

    print 'perplexity ',p_final
    return p_final

def get_at_results(vocab_file, topic_numbers, word_in_topic):
    ret = dict()
    ret['success'] = 1
    ret['message'] = 'success'
    ret['topics'] = []
    # randomly choose one type of panel
    panel_types = ('panel-primary','panel-success','panel-info','panel-warning','panel-danger')
    K = topic_numbers
    V = run_lda.read_vocab(vocab_file)
    phi = get_results()[K]['phi']

    for k in range(0, topic_numbers):
        this_topic = []

        topic_color = panel_types[random.randint(0,len(panel_types)-1)]
        print len(phi)
        phi_this_topic = [(i,phi[k][i]) for i in range(len(phi[k]))]
        phi_this_topic.sort(reverse=True,key=lambda k:k[1])
        for i in range(0, word_in_topic):
            word,freq = phi_this_topic[i]
#            TopicWord(topic=t, word=vocab[word], freq = "%.10f"%freq).save()
            this_topic.append([k, V[word], "%.6f"%freq, topic_color, u'未分类']) # add color
        ret['topics'].append(this_topic)

    return ret
