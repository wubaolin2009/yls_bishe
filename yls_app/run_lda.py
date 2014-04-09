# -*- coding: utf-8 -*-
#OUT_TOKENIZED_FOLDER = "/home/willw/bishe_weibo_tengxun/tokenized/"
VOCAB_FILE = "/home/willw/bishe_weibo_tengxun/wbl_80_converted"

import os
import cPickle, string, numpy, getopt, sys, random, time, re, pprint
import onlineldavb
import thread
from yls_app.models import *

# this option, when True, turned more verbose vocabulary
verbose_vocabulary = True
def calc_file_counts():
    global verbose_vocabulary
    if verbose_vocabulary:
        count = TweetToken.objects.count()
    else:
        count = TweetUserToken.objects.count()
    return count

file_counts = 0
g_all_files = []

def get_article(start,count):
    end = start + count
    if end > file_counts:
        end = file_counts

    contents = []
    global verbose_vocabulary
    if verbose_vocabulary:
        for file_name in TweetToken.objects.all()[start:end]:
            contents.append(file_name.tokens)
    else:
        for file_name in TweetUserToken.objects.all()[start:end]:
            contents.append(file_name.tokens)
    return contents

def test_get_file_contents():
    assert len(get_article(0, 64)) == 64
    assert len(get_article(64, 12)) == 12
    assert len(get_article(0, 1)) == 1
    assert len(get_article(0, 0)) == 0

def read_vocab(file_name):
    vocab = []
    f = open(file_name,'r').readlines()
    print 'read vocab %s, %d'%(file_name, len(f))
    for line in f:
        decoded = line.decode('utf-8')
        decoded = decoded.replace(u'\r\n', u'')
        decoded = decoded.replace(u'\n', u'')
        vocab.append(decoded)
    return vocab

#test_get_file_contents()


class LDARunner(object):
    @staticmethod
    def start_run_lda(meaningful_words_path, batchsize=2900000, K=80, GAMMA_ITER_TIMES=400):
#        thread.start_new_thread(LDARunner.run_lda, (meaningful_words_path, batchsize, K, GAMMA_ITER_TIMES))
        LDARunner.run_lda(meaningful_words_path, batchsize, K, GAMMA_ITER_TIMES)

    LAMBDA_FILE = 'yls_app/tools/lambda.dat'
    GAMMA_FILE = 'yls_app/tools/gamma.dat'
    # The number of documents to analyze each iteration
    # batchsize = 500
    # The total number of documents in Wikipedia
    # D = file_counts
    # The number of topics
    # K = 150
    # Gamma iteration times 
    # GAMMA_ITER_TIMES = 1000
    @staticmethod
    def run_lda(meaningful_words_path, batchsize, K, GAMMA_ITER_TIMES):
        t = Task.create_new_lda_task()
        global file_counts, g_all_files
        file_counts = calc_file_counts()
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
            print 'target iteration %d'%(documentstoanalyze)
            # Our vocabulary, we didn't use vocabulary.
            vocab = read_vocab(meaningful_words_path) 

            # Keep track of the last iteration
            last_iteration_perplexity = 0.0

            # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
            olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7, GAMMA_ITER_TIMES)
            # Run until we've seen all documents.
            for iteration in range(documentstoanalyze):
                print 'iteration ... %d'%iteration
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
                print 'perplexity: %f'%(last_iteration_perplexity)

                # Save lambda, the parameters to the variational distributions
                # over topics, and gamma, the parameters to the variational
                # distributions over topic weights for the articles analyzed in
                # the last iteration.
                #if (iteration % 10 == 0):
                    #numpy.savetxt('lambda-%d.dat' % iteration, olda._lambda)
                    #numpy.savetxt('gamma-%d.dat' % iteration, gamma)
                    #
                numpy.savetxt(LDARunner.LAMBDA_FILE, olda._lambda)
                numpy.savetxt(LDARunner.GAMMA_FILE, gamma)
        except Exception,e:
            print e
            t.infomation = "Exception:" + e.message
            Task.finish_task(t, False)
        t.infomation = "Successful! Perplexity:" + str(last_iteration_perplexity)
        Task.finish_task(t, True)

    @staticmethod
    def clear_topic_result():
        TopicWord.objects.all().delete()
        Topic.objects.all().delete()

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

        for i in [labmda_file_name, vocab_file]:
            if not os.path.exists(i):
                ret['success'] =  0
                ret['message'] = i + " not exists!"
                return ret

        vocab = read_vocab(vocab_file)
        testlambda = numpy.loadtxt(labmda_file_name)

        if topic_numbers > len(testlambda):
            topic_numbers = len(testlambda)

        for k in range(0, topic_numbers):
            this_topic = []
            lambdak = list(testlambda[k, :])
            lambdak = lambdak / sum(lambdak)
            temp = zip(lambdak, range(0, len(lambdak)))
            temp = sorted(temp, key = lambda x: x[0], reverse=True)
            print 'topic %d:' % (k)
            t = Topic(topic_id=k, topic_name=u'未分类')
            t.save()
            # feel free to change the "53" here to whatever fits your screen nicely.
            topic_color = panel_types[random.randint(0,len(panel_types)-1)]
            for i in range(0, word_in_topic):
                TopicWord(topic=t, word=vocab[temp[i][1]], freq = "%.10f"%temp[i][0]).save()
                this_topic.append([k, vocab[temp[i][1]], "%.4f"%temp[i][0], topic_color, u'未分类']) # add color
            ret['topics'].append(this_topic)

        return ret

if __name__ == '__main__':
    #main()
    #print_result('lambda-30.dat')
    pass
