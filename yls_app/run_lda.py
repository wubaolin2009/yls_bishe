# -*- coding: utf-8 -*-
#OUT_TOKENIZED_FOLDER = "/home/willw/bishe_weibo_tengxun/tokenized/"
VOCAB_FILE = "/home/willw/bishe_weibo_tengxun/wbl_80_converted"

import os
import cPickle, string, numpy, getopt, sys, random, time, re, pprint
import onlineldavb
import thread
from yls_app.models import *

def calc_file_counts():
    files = []
    count = TweetUserToken.objects.count()
    for w in TweetUserToken.objects.all():
        files.append(w.user.name)
    return count, files

file_counts = 0
g_all_files = []

def get_article(start,count):
    end = start + count
    if end > file_counts:
        end = file_counts
    file_lists = g_all_files[start:end]
    contents = []
    for file_name in file_lists:
        file_content = TweetUserToken.objects.filter(user_name=file_name)[0].tokens
        contents.append(file_content)
    return contents

def test_get_file_contents():
    assert len(get_article(0, 64)) == 64
    assert len(get_article(64, 12)) == 12
    assert len(get_article(0, 1)) == 1
    assert len(get_article(0, 0)) == 0

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


class LDARunner(object):
    @staticmethod
    def start_run_lda(tokenized_folder, meaningful_words_path, batchsize=128, K=100, GAMMA_ITER_TIMES=500):
        thread.start_new_thread(LDARunner.run_lda, (tokenized_folder, meaningful_words_path, batchsize, K, GAMMA_ITER_TIMES))

    LAMBDA_FILE = 'lambda.dat'

    # The number of documents to analyze each iteration
    # batchsize = 500
    # The total number of documents in Wikipedia
    # D = file_counts
    # The number of topics
    # K = 150
    # Gamma iteration times 
    # GAMMA_ITER_TIMES = 1000
    @staticmethod
    def run_lda(tokenized_folder, meaningful_words_path, batchsize, K, GAMMA_ITER_TIMES):
        t = Task.create_new_lda_task()
        global file_counts, g_all_files
        file_counts, g_all_files = calc_file_counts(tokenized_folder)
        D = file_counts
        t.status = Task.TASK_STATUS_STARTED
        t.save()

        try: 
            # Remove the formmer results
            # TODO: save it in dababases
            os.popen("rm yls_app/tools/lambda*")
            os.popen("rm yls_app/tools/gamma*")
            # How many documents to look at
            documentstoanalyze = int(D/batchsize) + 1

            # Our vocabulary, we didn't use vocabulary.
            vocab = read_vocab(meaningful_words_path)    

            # Keep track of the last iteration
            last_iteration_perplexity = 0.0

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
                t.infomation = '%d:  rho_t = %f,  held-out perplexity estimate = %f' % \
                    (iteration, olda._rhot, numpy.exp(-perwordbound))

                last_iteration_perplexity = numpy.exp(-perwordbound)

                t.status = Task.TASK_STATUS_STARTED
                t.save()

                # Save lambda, the parameters to the variational distributions
                # over topics, and gamma, the parameters to the variational
                # distributions over topic weights for the articles analyzed in
                # the last iteration.
                #if (iteration % 10 == 0):
                    #numpy.savetxt('lambda-%d.dat' % iteration, olda._lambda)
                    #numpy.savetxt('gamma-%d.dat' % iteration, gamma)
                    #
                numpy.savetxt(LDARunner.LAMBDA_FILE, olda._lambda)
                numpy.savetxt('gamma.dat', gamma)
        except Exception,e:
            t.infomation = "Exception:" + e.message
            Task.finish_task(t, False)
        t.infomation = "Successful! Perplexity:" + str(last_iteration_perplexity)
        Task.finish_task(t, True)
     
    @staticmethod   
    def get_result(vocab_file, topic_numbers, word_in_topic, labmda_file_name = LAMBDA_FILE):
        ''' return type:
        { 
        success: 0,
        message: '' if it's failed,
        topics:[ [[topic_id, word1,freq1],[topic_id, word2,freq2], ]
        } '''
        ret = dict()
        ret['success'] = 1
        ret['message'] = 'success'
        ret['topics'] = []
        for i in [labmda_file_name, vocab_file]:
            if not os.path.exists(i):
                ret['success'] =  0
                ret['message'] = i + " not exists!"
                return ret

        vocab = read_vocab(vocab_file)
        testlambda = numpy.loadtxt(labmda_file_name)

        if topic_numbers > len(testlambda):
            topic_numbers = len(testlambda)

        # randomly choose one type of panel
        panel_types = ('panel-primary','panel-success','panel-info','panel-warning','panel-danger')

        for k in range(0, topic_numbers):
            this_topic = []
            lambdak = list(testlambda[k, :])
            lambdak = lambdak / sum(lambdak)
            temp = zip(lambdak, range(0, len(lambdak)))
            temp = sorted(temp, key = lambda x: x[0], reverse=True)
            print 'topic %d:' % (k)
            # feel free to change the "53" here to whatever fits your screen nicely.
            topic_color = panel_types[random.randint(0,len(panel_types)-1)]
            for i in range(0, word_in_topic):
                this_topic.append([k, vocab[temp[i][1]], "%.4f"%temp[i][0], topic_color]) # add color
            ret['topics'].append(this_topic)

        return ret

if __name__ == '__main__':
    #main()
    #print_result('lambda-30.dat')
    pass