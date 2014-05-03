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

