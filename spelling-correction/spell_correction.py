import re
import numpy as np
import math


with open('vocab.txt', 'r') as f:
    VOCAB = [line.strip() for line in f.readlines()]
with open('big.txt') as f:
    text = f.read()
diction = re.findall('[a-z]+',text.lower())
with open('model.lm') as f:
    lines = [line.split() for line in f.readlines()]
PROB1 = lines[20264:-2]
with open('count_1edit.txt', encoding='UTF-8') as f:
    lines = f.readlines()
confuse_matrix = np.array([line.split('\t') for line in lines])
SUM = sum([float(num.split()[0]) for num in confuse_matrix[:,1]])
confuse_matrix[:,1] = [float(num.split()[0])/SUM for num in confuse_matrix[:,1]]

def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):

    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))


def edittype(word,error):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    word,error = word.lower(),error.lower()
    for i in range(len(word)):
        if word == error[1:]:
            return error[0]+'|<s>', 'ins'
        if word[1:] == error:
            return '|'+word[0], 'del'
        if i >= len(error):
            return word[i]+'|'+error[i-1]+word[i], 'del'
        elif word[i] != error[i]:
            if word in [error[:i]+k+error[i:] for k in letters]:
                return error[i-1]+'|'+error[i-1]+word[i], 'del'
            elif word in [error[:i]+k+error[i+1:] for k in letters]:
                return error[i]+'|'+word[i], 'sub'
            elif word == error[:i]+error[i+1:] or word == error[:-1]:
                return word[i-1]+error[i]+'|'+word[i-1], 'ins'
            elif word[i]+ word[i+1] == error[i+1]+error[i]:
                return word[i+1]+word[i]+'|'+word[i]+word[i+1], 'trans'
    if len(word)<len(error):
        return word[-1]+error[-1]+'|'+word[-1], 'ins'


def known(words):

    return set(word for word in words if word in VOCAB)

def bigram(word_front, word):
    flag = 0
    result = 0
    for each in PROB1:
        if ((each[1] == word_front) or (each[1].lower() == word_front)) and ((each[2] == word ) or (each[2].lower()== word)):
            result = result + float(each[0])
            flag = 1
    if flag == 0:
        result = -1000
    return result


def prob1(word, error, line):
    new_line = line.replace(error, word)
    new_line = re.findall('[a-z]+', new_line)
    index = new_line.index(word)
    if index in range(1,len(new_line)-1):
        word_front = new_line[index - 1]
        word_back = new_line[index + 1]
    elif index == 0:
        word_front = '<s>'
        word_back = new_line[index + 1]
    else :
        word_front = new_line[index - 1]
        word_back = '</s>'
    return bigram(word_front, word) + bigram(word, word_back)


def prob2(error, word):
    route = edittype(word, error)
    for each in confuse_matrix:
        if route[0] == each[0]:
            return math.log(float(each[1]))
    # 0:deletes, 1:transposes, 2:replaces, 3:inserts

def non_word_correct(error, line):
    candidates = known(edits1(error)) | set(list([error]))
    # print(candidates)
    if len(candidates)==1:
        candidates = candidates | known(edits2(error))
    p_flag = -100000
    right = error
    for candidate in candidates:
        # print(candidate)
        p = prob1(candidate, error, line) #* prob2(error, candidate)
        # print(candidate,p)
        if p > p_flag:
            p_flag = p
            right = candidate
        # print(right)
    return right

def real_word_correct(sentence):
    length = len(sentence)
    correction = []
    p_flag_in = -100000
    p_flag_out = -100000
    word_flag = ''
    candidate_flag_in = ''
    candidate_flag_out = ''

    for word in sentence:
        if len(word) > 2:
            print('word:',word)
            candidates = known(edits1(word)) | set(list([word]))
            print('candidates_edits1:',candidates)
            '''
            if len(candidates)==1:
                candidates = candidates | known(edits2(word))
            print('candidates_edits2:',candidates)
            '''
            i = sentence.index(word)
            for candidate in candidates:
                sentence1 = sentence.copy()
                sentence1[i] = candidate
                p = bigram('<s>', sentence1[0]) + bigram(sentence1[-1], '</s>') + sum([bigram(sentence1[i], sentence1[i+1]) for i in range(length-1)])
                if p > p_flag_in:
                    p_flag_in = p
                    candidate_flag_in = candidate
            print('candidate_flag_in:',candidate_flag_in)
            print('p_flag_in:',p_flag_in)
            print('_______________________')
            if p_flag_in > p_flag_out:
                p_flag_out = p_flag_in
                candidate_flag_out = candidate_flag_in
                word_flag = word
    return word_flag,candidate_flag_out

#print(real_word_correct(re.findall('[a-z]+', 'what do you like')))

def train():
    with open('testdata.txt') as f:
        lines = f.readlines()
    f = open('result.txt','w+')
    lines_lower = [line.lower() for line in lines]
    print('lines_lower')
    for i in range(len(lines_lower)):
        line = lines_lower[i]
        sentence = re.findall('[a-z]+', line)
        errors = []
        for word in sentence:
            if word not in VOCAB:
                errors.append(word)
        print('errors:',errors)
        for error in errors:
            print(error)
            if len(error) > 1:
                right = non_word_correct(error, line)
                lines[i] = lines[i].replace(error, right, 1)
                print("right:",right)
        print('noneword')
        '''
        error, right = real_word_correct(sentence)
        print('realword')
        lines[i].replace(error, right, 1)
        '''
        f.writelines(lines[i])
        print(i)
    f.close


train()
# print(non_word_correct("busines", "We wouldn't be able to do busines, said a spokesman for  leading Japanese electronics firm Matsushita Electric  Industrial Co Ltd ltMC.T."))
