# -*- coding: utf-8 -*-
# This file implements Author Topic LDA
# data sources
from yls_app.models import *
import numpy
import random
import os
import run_lda
import bisect
# parameters for AT-LDA
K = 80
alpha = 1.0/K
beta = 0.01

def cal_na(nak,a):
    return sum(nak[a])

def cal_nk(nkw,k):
    return sum(nkw[k])

def save_phi(phi):
    outfile = open('yls_app/phi_result','w')
    for a in phi:
        for b in a:
            outfile.write((u'%f '%b).encode('utf-8'))
        outfile.write((u'\n').encode('utf-8'))
    outfile.close()
    
def get_phi():
    infile = open('yls_app/phi_result','r')
    phi = []
    for m in infile.readlines():
        e = []
        for entry in m.decode('utf-8').replace(u'\n',u'').split(u' '):
            e.append(entry)
        phi.append(e)
    return phi

def save_sita(sita):
    outfile = open('yls_app/sita_result','w')
    for a in sita:
        for b in a:
            outfile.write((u'%f '%b).encode('utf-8'))
        outfile.write((u'\n').encode('utf-8'))
    outfile.close()
    
def get_sita(sita):
    infile = open('yls_app/sita_result','r')
    phi = []
    for m in infile.readlines():
        e = []
        for entry in m.decode('utf-8').replace(u'\n',u'').split(u' '):
            e.append(entry)
        sita.append(e)
    return sita

def get_KAmn():
    infile = open('yls_app/kmn_result','r')
    Kmn = []
    for m in infile.readlines():
        e = []
        for entry in m.decode('utf-8').replace(u'\n',u'').split(u' '):
            if len(entry) == 0:
                continue
            print entry
            e.append(int(float(entry)))
        Kmn.append(e)
    infile = open('yls_app/amn_result','r')
    Amn = []
    for m in infile.readlines():
        e = []
        for entry in m.decode('utf-8').replace(u'\n',u'').split(u' '):
            if len(entry) == 0:
                continue
            e.append(int(float(entry)))
        Amn.append(e)
    return Kmn,Amn

def save_KAmn(KK,AA):
    outfile = open('yls_app/kmn_result','w')
    for a in KK:
        for b in a:
            outfile.write((u'%f '%b).encode('utf-8'))
        outfile.write((u'\n').encode('utf-8'))
    outfile.close()
    outfile = open('yls_app/amn_result','w')
    for a in AA:
        for b in a:
            outfile.write((u'%f '%b).encode('utf-8'))
        outfile.write((u'\n').encode('utf-8'))
    outfile.close()

def at_lda():
    all_author_token = []

    # get the vocabulary file
    V = run_lda.read_vocab('yls_app/tools/wbl_80_converted_manual_processed')
    Vset = set(V)

    # Read all authors and their tokens
    print 'load all the tokens'
    for entry in TweetUserToken.objects.all()[0:200]:
        author = entry.user_name
        tokens = entry.tokens
        tokens = filter(lambda k:k in Vset, tokens.split(u' '))
        all_author_token.append((author,tokens))

    all_authors = [m[0] for m in all_author_token]
#   all_author_token = [m[1] for m in all_author_token]

    # numpy.random.multinomial(10,[0.1,0.1,0.8])
    # numpy.random.dirichlet((10, 5, 3), 1)

    # store tha topic
    Kmn = []
    # store the author
    Amn = []
    print 'init Kmn and Amn'
    if not os.path.exists('yls_app/kmn_result'):
        for m in all_author_token:
            author,tokens = m
            Kmn.append([-1 for i in range(len(tokens))])
            Amn.append([-1 for i in range(len(tokens))])
    else:
        print 'read from cached_data'
        Kmn,Amn = get_KAmn()

    print 'Tokens number are %d'%(sum(map(len,Kmn)))
        
    #Init All K and A randomly
    for m in range(len(Kmn)):
        for n in range(len(Kmn[m])):
            Kmn[m][n] = random.randint(0,K-1)
            Amn[m][n] = random.randint(0,len(all_authors)-1)

    nak = [[-1 for m in range(K)] for i in range(len(all_authors))]
    nkw = [[-1 for w in range(len(V))] for i in range(K)]
    na = [cal_na(nak,a) for a in range(len(all_authors))]
    nk = [cal_nk(nkw,k) for k in range(K)]

    def sample_k_a(w):
        LENA = len(all_authors)
        p = [0] * (LENA*K)
        for k in range(K):
            pre = (nkw[k][w] + beta)/float(nk[k]+len(V)*beta)
            for a in range(LENA):
                index = k*LENA + a
                p[index] = (nak[a][k]+alpha)/(na[a]+K*alpha) * pre
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

    for iteration in range(0,4):
        print 'iteration %d'%(iteration)
        for m in range(len(Kmn)):
            print 'processing doc %d tokens %d'%(m,len(all_author_token[m][1]))
            for w_index in range(len(Kmn[m])):
                w = bisect.bisect_right(V,all_author_token[m][1][w_index]) - 1
                k,a = Kmn[m][w_index],Amn[m][w_index]
                nak[a][k],na[a],nkw[k][w],nk[k] = nak[a][k]-1,na[a]-1,nkw[k][w]-1,nk[k]-1
                #sample new topic k, and author a
                new_k,new_a = sample_k_a(w)
                #new_k,new_a = 1,1
                Kmn[m][w_index] = new_k
                Amn[m][w_index] = new_a
                #update nak, na, nkw,nk
                nak[new_a][new_k],na[new_a],nkw[new_k][w],nk[new_k] = nak[new_a][new_k]-1,na[new_a]-1,nkw[new_k][w]-1,nk[new_k]-1

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

#       save_phi(phi)
#       save_sita(sita)
#       save_KAmn(Kmn,Amn)
