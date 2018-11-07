import nltk
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def conbain_txt(train):
    pass


def tfidf(str1, str2):
    X_test = [str1, str2]
    tfidf = TfidfVectorizer()
    weight = tfidf.fit_transform(X_test).toarray()
    word = tfidf.get_feature_names()
    for i in range(len(weight)):
    # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，
    # 第二个for便利某一类文本下的词语权重
        print(u"-------这里输出第", i, u"类文本的词语tf-idf权重------")
        for j in range(len(word)):
            print(word[j], weight[i][j]) # 第i个文本中，第j个次的tfidf值


def train_sample(train, news):
    for i in range(len(train)):
        id_str = train[i][1].split(',')
        id_list = [int(i) for i in id_str]
        title_list = []
        content_list = []
        for j in range(len(news)):
            a = news[j]
            content = a['content']
            title = a['title']
            id = a['id']
            if id in id_list:
                title_list.append(title)
                content_list.append(content)
        train[i].append(title_list)
        train[i].append(content_list)
        instance = train[i]
        train[i] = (features(instance[3]),instance[0])
    return train


def test_sample(test, news, flag=0):
    test_copy = test.copy()
    for i in range(len(test_copy)):
        id_str = test_copy[i][1].split(',')
        id_list = [int(i) for i in id_str]
        title_list = []
        content_list = []
        for j in range(len(news)):
            a = news[j]
            content = a['content']
            title = a['title']
            id = a['id']
            if id in id_list:
                title_list.append(title)
                content_list.append(content)
        test_copy[i].append(title_list)
        test_copy[i].append(content_list)
        if flag == 0:
            instance = test_copy[i]
            test_copy[i] = (features(instance[2]),instance[0])
    return test_copy


def features(words): #特征提取器

    f = open('stopwords.txt', mode='r', encoding='utf-8')
    stopWords = [i for i in f.read() if i != '\n']
    f.close()

    result = []
    for i in range(len(words)):
        s = words[i]
        cut = jieba.cut(s)
        cut = ' '.join(cut)
        cut = cut.split()
        temp = []
        for word in cut:
            if word not in stopWords:
                temp.append(word)
        result = result + temp
        break
    return dict([(word, True) for word in result])


def main():
    f = open('news.txt', mode='r', encoding='utf-8')
    news = [eval(i) for i in f.readlines()]
    f.close()

    f = open('train.txt', mode='r', encoding='utf-8')
    train = [i.split() for i in f.readlines()]
    f.close

    f = open('test.txt', mode='r', encoding='utf-8')
    test = [i.split() for i in f.readlines()]
    f.close

    train = train_sample(train, news)
    print('--------------------------------------------------------')

    classifier = nltk.NaiveBayesClassifier.train(train) #生成分类器

    test1 = test_sample(test, news)
    print(test1[0])

    f = open('result.txt', 'w')
    for i in range(len(test1)):
        tag = classifier.classify(test1[i][0])#分类
        f.write(tag+' '+test[i][1]+'\n')
    f.close()


    # print(nltk.classify.accuracy(classifier,test)) #测试准确度

    classifier.show_most_informative_features(5)#得到似然比，检测对于哪些特征有用


if __name__ == '__main__':
    main()
