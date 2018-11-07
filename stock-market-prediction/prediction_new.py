import nltk
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


f = open('news.txt', mode='r', encoding='utf-8')
news = [eval(i) for i in f.readlines()]
f.close()

f = open('train.txt', mode='r', encoding='utf-8')
train = [i.split() for i in f.readlines()]
f.close

f = open('test.txt', mode='r', encoding='utf-8')
test = [i.split() for i in f.readlines()]
f.close

f = open('stopwords.txt', mode='r', encoding='utf-8')
stopWords = [i for i in f.read() if i != '\n']
f.close()

def content(test, news):
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
        test_copy[i][1] = content_list
        # test_copy[i].append(title_list)
        # test_copy[i].append(content_list)
    return test_copy
'''
new_train = content(train, news)
new_test = content(test, news)
print(type(new_test),len(new_test),
    type(new_test[0]),len(new_test[0]))
'''

def del_stopword(train):
    for each in train:
        result = ''
        for sentence in each[1]:
            cut = jieba.cut(sentence)
            cut = ' '.join(cut)
            cut = cut.split()
            temp = ''
            for word in cut:
                if word not in stopWords:
                    temp = temp + word + ' '
            result = result + temp
        each[1] = result

print(del_stopword(content(train, news)))


def txt2str(train):
    str1, str2 = '', ''
    for each in train:
        if each[0] == '+1':
            str1 = str1 + each[1]
        elif each[0] == '-1':
            str2 = str2 + each[1]
    return [str1, str2]



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

    return weight


train = del_stopword(content(train, news))
[str1, str2] = txt2str(train)
tfidf(str1, str2)

def prepare(train):
    for each in train:
        temp = []
        words = each[1].split()
        for word in words:
            if word in vocab:
                temp.append(word)
        each[1] = each[0]
        each[0] = dict([(word, True) for word in temp])
    return train


classifier = nltk.NaiveBayesClassifier.train(train) #生成分类器


test = prepare(del_stopword(content(test, news)))
print(test[0])

f = open('result.txt', 'w')
for i in range(len(test1)):
    tag = classifier.classify(test[i][0])#分类
    f.write(tag+' '+test[i][1]+'\n')
f.close()


