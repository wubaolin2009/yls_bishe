# -*- coding: utf-8 -*-
OUT_TOKENIZED_FOLDER = "/home/willw/bishe_weibo_tengxun/tokenized/"
VOCAB_FILE = "/home/willw/bishe_weibo_tengxun/wbl_80_converted"


import os
import cPickle, string, numpy, getopt, sys, random, time, re, pprint
import onlineldavb

def calc_file_counts(path):
    files = []
    count = 0
    for a,b,f in os.walk(path):
        for w in f:
            count += 1
            files.append(path + w)
    return count, files

file_counts, g_all_files = calc_file_counts(OUT_TOKENIZED_FOLDER)

# The number of documents to analyze each iteration
batchsize = 500
# The total number of documents in Wikipedia
D = file_counts
# The number of topics
K = 150
# Gamma iteration times 
GAMMA_ITER_TIMES = 1000

def get_article(start,count):
    end = start + count
    if end > file_counts:
        end = file_counts
    file_lists = g_all_files[start:end]
    contents = []
    for file_name in file_lists:
        f = open(file_name, 'r')
        file_content = u""
        for line in f.readlines():
            line = line.decode('utf-8').replace(u'\r\n',u'')
            if len(line) <= 1:
                continue
            file_content += ( line + u' ')
        contents.append(file_content)
    return contents

def test_get_file_contents():
    assert len(get_article(OUT_TOKENIZED_FOLDER, 0, 64)) == 64
    assert len(get_article(OUT_TOKENIZED_FOLDER, 64, 12)) == 12
    assert len(get_article(OUT_TOKENIZED_FOLDER, 0, 1)) == 1
    assert len(get_article(OUT_TOKENIZED_FOLDER, 0, 0)) == 0

def read_vocab(file_name):
    vocab = []
    f = open(file_name,'r').readlines()
    for line in f:
        decoded = line.decode('utf-8')
        decoded = decoded.replace(u'\r\n', u'')
        decoded = decoded.replace(u'\n', u'')
        vocab.append(decoded)
    return vocab

#test_get_file_contents()

def main():
    """
    Downloads and analyzes a bunch of random Wikipedia articles using
    online VB for LDA.
    """
    global batchsize, D, K    

    # How many documents to look at
    documentstoanalyze = int(D/batchsize) + 1

    # Our vocabulary, we didn't use vocabulary.
    vocab = read_vocab(VOCAB_FILE)    

    # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7, GAMMA_ITER_TIMES)
    # Run until we've seen all documents.
    for iteration in range(documentstoanalyze):
        # Download some articles
        docset = get_article(iteration * batchsize, batchsize)
        # Give them to online LDA
        (gamma, bound) = olda.update_lambda(docset)
        # Compute an estimate of held-out perplexity
        (wordids, wordcts) = onlineldavb.parse_doc_list(docset, olda._vocab)
        perwordbound = bound * len(docset) / (D * sum(map(sum, wordcts)))
        print '%d:  rho_t = %f,  held-out perplexity estimate = %f' % \
            (iteration, olda._rhot, numpy.exp(-perwordbound))

        # Save lambda, the parameters to the variational distributions
        # over topics, and gamma, the parameters to the variational
        # distributions over topic weights for the articles analyzed in
        # the last iteration.
        if (iteration % 10 == 0):
            numpy.savetxt('lambda-%d.dat' % iteration, olda._lambda)
            numpy.savetxt('gamma-%d.dat' % iteration, gamma)

def print_result(labmda_file_name):
    vocab = read_vocab(VOCAB_FILE)
    testlambda = numpy.loadtxt(labmda_file_name)

    for k in range(0, len(testlambda)):
        lambdak = list(testlambda[k, :])
        lambdak = lambdak / sum(lambdak)
        temp = zip(lambdak, range(0, len(lambdak)))
        temp = sorted(temp, key = lambda x: x[0], reverse=True)
        print 'topic %d:' % (k)
        # feel free to change the "53" here to whatever fits your screen nicely.
        for i in range(0, 40):
            print '%20s  \t---\t  %.4f' % (vocab[temp[i][1]], temp[i][0])
        print

if __name__ == '__main__':
    #main()
    print_result('lambda-30.dat')
    pass