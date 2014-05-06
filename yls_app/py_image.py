# this file is used to store the image generation code
# of this bishe
import matplotlib.pyplot as plt

def draw_cos_rec_score_image():
    xx = range(20)

    result_cos = [179,50,172,265,142,250,117,86,165,75,163,234,139,61,78,177,215,91,102,168]
    result_cos = map(lambda k:k/75.0, result_cos) 


    for i in range(len(result_cos)):
        plt.bar(1 + i - 0.25, result_cos[i], 0.5, bottom=0.001,label='aaa')

    plt.xlabel('user')
    plt.ylabel('score')
    plt.title("Score of Recommendation")
    plt.gca().set_ylim((0.001,4.0))
    plt.gca().set_xticks(range(1,21))
    plt.show()

def draw_KL_rec_score_image():
    xx = range(20)

    delta = [-2.2,0.1,-1.9,0.2,0.4,2,0.2,0.1,5,2.1,2.87,-1.1,2.9,0.5,1.2,-0.2,2.3,-0.5,2.5,7]
    delta_2 = [-2.1,-0.0,-0.0,-0.0,1.1, \
             0.0, 0.0,0.0,1.0,0.0, \
             -1, 0.0, 0.0, 2.0, -1.0,\
             0.0, 0.0, 0.0, 0.0,0.0 ] 

    delta = map(lambda k:k*5, delta)
    delta_2 = map(lambda k:k*5, delta_2)

    label1,label2 = plt.plot(xx,delta,'r.-', xx,delta_2,'g-.')
    label1.set_label('KL')
    label2.set_label('Euclid')
    plt.legend(loc='upper left',shadow=True)
    plt.xlabel('weibo user')
    plt.ylabel('score difference')
    plt.title("Score Recommendation diff")
    plt.gca().set_ylim((-20,40))
    plt.gca().set_xticks(range(1,21))
    plt.show()
    



def draw_cos_rec_socre_sperately_for_user2():
    xx = range(15)

    result_cos = [1.4,2.8,0.2,1.2,0.2,0.2,0.6,1,0,0,0.2,0.6,0.8,0,0.8]


    for i in range(len(result_cos)):
        plt.bar(1 + i - 0.25, result_cos[i], 0.5, bottom=0.001,label='aaa')

    plt.xlabel('user')
    plt.ylabel('score')
    plt.title("Score for User #2")
    plt.gca().set_ylim((0.001,3.0))
    plt.gca().set_xticks(range(1,16))
    plt.show()

def draw_perplexity():
    xx = range(10,120,10)

    perplextity_lda = [2563,2711,2817,1950,2952,2884,2968,2938,2911,2904,3032]

    perplexity_at = [2189.75,2357,2523,2356,2251,2171,2036,2626,1988,2672,2135]
 
    perplexity_iat = [2011, 2210, 2322, 1988, 2107, 2007, 2221, 2271, 2377, 2035, 2271]

    label1,label2,label3 = plt.plot(xx,perplextity_lda ,'r.-', xx,perplexity_at,'g-.',xx,perplexity_iat, 'b*-')
    label1.set_label('LDA')
    label2.set_label('AT')
    label3.set_label('IAT')

    plt.legend(loc='upper left',shadow=True)
    plt.xlabel('Topic Number')
    plt.ylabel('Perplexity')
    plt.title("Topic Model Perplexity")
    plt.gca().set_ylim((1500,3100))
    plt.gca().set_xticks(range(10,120,10))
    plt.show()


def draw_score_topic():
xx = [10,20,30,40,50]

perplextity_lda = [0.42,0.41,0.33,0.32,0.31]

perplexity_at = [0.56,0.67,0.60, 0.81, 0.68]
 
perplexity_iat = [0.61,0.71, 0.52, 0.83, 0.62]

label1,label2,label3 = plt.plot(xx,perplextity_lda ,'r.-', xx,perplexity_at,'g-.',xx,perplexity_iat, 'b*-')
label1.set_label('LDA')
label2.set_label('AT')
label3.set_label('IAT')

plt.legend(loc='upper left',shadow=True)
plt.xlabel('Topic Number')
plt.ylabel('Score')
plt.title("Topic Model Score")
plt.gca().set_ylim((0.2,1.0))
plt.gca().set_xticks(range(10,60,10))
plt.show()

def draw_score_topic_rec_cos_lda_at_iat():
xx = range(20)
result_cos = [179,50,172,265,142,250,117,86,165,75,163,234,139,61,78,177,215,91,102,168]
result_cos = map(lambda k:k/75.0, result_cos) 
perplextity_lda = [80,40,110,137,133,107,135,78,121,112,132,137,62,85,71,121,39,56,110,49]
perplextity_lda = map(lambda k:k/75.0, perplextity_lda)
perplexity_at = [139,121,158, 167,117,193,165,126,79,95,89,150,150,145,60,149,137,127,147, 121]
perplexity_at = map(lambda k:k/75.0, perplexity_at)
perplexity_iat = result_cos

label1,label2,label3 = plt.plot(xx,perplextity_lda ,'r.-', xx,perplexity_at,'g-.',xx,perplexity_iat, 'b*-')
label1.set_label('LDA')
label2.set_label('AT')
label3.set_label('IAT')

plt.legend(loc='upper left',shadow=True)
plt.xlabel('Weibo User Index')
plt.ylabel('Score')
plt.title("Recommendation Score")
plt.gca().set_ylim((0.2,4.0))
plt.gca().set_xticks(range(0,21))
plt.show()

#this code is used to generate the recommended results' histogram
import pickle
f = open('goods_hit_results','r')
a = pickle.load(f)
f.close()

m = [a[k] for k in a.keys() if a[k] > 0]

numbins = 20

import matplotlib.pyplot as plt

#xx = range(8)
#result_cos = [213, 41, 21, 16, 3, 17, 5, 14]
n, bins, patches = plt.hist(m, numbins , facecolor='green', alpha=0.5)
plt.xlabel('Recommended times')
plt.ylabel('number of goods')
plt.title("Histogram of Recommendation")
#plt.gca().set_ylim((0.001,214))
#plt.gca().set_xticks(['a','b'])
plt.show()

##############################################
#codes to generate the running time of AT, LDA, and IAT
import matplotlib.pyplot as plt

K = 

LDA_ITERATION_TIME = [3.2,4.1,5.7,6.8,7.52]
AT_ITERATION_TIME = [3.2 * 36, 4.1 * 42, 5.1 * 31, 6.5 * 39, 7.2 * 34]
IAT_ITERATION_TIME = [3.2*12,4.1*21, 5.1*13, 6.5 * 19.6, 7.2 * 14]

LDA_ITERATION_TIME = map(lambda k:k*2000, LDA_ITERATION_TIME)
AT_ITERATION_TIME = map(lambda k:k*2000, AT_ITERATION_TIME)
IAT_ITERATION_TIME = map(lambda k:k*2000, IAT_ITERATION_TIME)

label1,label2,label3 = plt.plot(K,LDA_ITERATION_TIME ,'r.-', K,AT_ITERATION_TIME,'g-.',K,IAT_ITERATION_TIME, 'b*-')
label1.set_label('LDA')
label2.set_label('AT')
label3.set_label('IAT')

plt.legend(loc='lower center',shadow=True)
plt.xlabel('Topic Number')
plt.ylabel('Finish Time(s)')
plt.title("Topic Model Perplexity: Iteration 2000,Author Number 40")
#plt.gca().set_ylim((1500,3100))
#plt.gca().set_xticks(range(10,120,10))
plt.yscale('log')
plt.show()


############################################
# codes to draw statisfactory image of Topic extraction
LDA = [5,4,2,2,3,2,3,4,3,3,2,3,5,5,2,5,3,1,1,5,4,2,2,3,5,3,3,1,2,4]
AT = [
