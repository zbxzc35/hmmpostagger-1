# This code should help get you started, but it is not guaranteed to
# be bug free!  If you find problems, please report to
# compling-class@cs.umass.edu

import re

from dicts import DefaultDict
from random import choice

def Dict(**args): 
    """Return a dictionary with argument names as the keys, 
    and argument values as the key values"""
    return args

def hmm(training_sentences, reducedtagset):
    """Given a list of pre-tagged sentences, return an HMM tuple containing
    the transition (1) and emission (2) probabilities"""
    transitions = DefaultDict(DefaultDict(0))
    emissions = DefaultDict(DefaultDict(0))
    wordcounts = DefaultDict(0)
    tagcounts = DefaultDict(0)

    for line in training_sentences:
	prevtag = '<START>'   # Before each sentence, begin in START state
        tagcounts['<START>'] += 1
	for taggedword in line.split():
	    (word, tag) = re.split('(?<!\\\)\/', taggedword)

            if reducedtagset:
            	if re.match('VB', tag) is not None: tag = 'VB'
            	elif re.match('NN', tag) is not None: tag = 'NN'
           	elif re.match('JJ', tag) is not None: tag = 'JJ'
            	elif re.match('RB', tag) is not None: tag = 'RB'

	    transitions[prevtag][tag] += 1
	    emissions[tag][word] += 1
	    wordcounts[word] += 1
            tagcounts[tag] += 1
            prevtag = tag

    print emissions.keys()
    
    return hmmtuple(transitions, emissions, wordcounts, tagcounts)

def hmmtuple(transitions, emissions, wordcounts, tagcounts):    
    # At test time we will need estimates for "unknown words"---the words
    # the words that never occurred in the training data.  One recommended
    # way to do this is to turn all training words occurring just once 
    # into '<UNKNOWN>' and use this as the stand-in for all "unknown words"
    # at test time.  Below we make all the necessary transformations
    # to '<UNKNOWN>'.
    for tag,dict in emissions.items():
	for word,count in dict.items():
	    if wordcounts[word] == 1:
		del emissions[tag][word]
		emissions[tag]['<UNKNOWN>'] += 1

    # Calculate smoothed conditional probabilities
    tags = emissions.keys()
    words = wordcounts.keys()

    for prevtag in transitions.keys():
        for tag in tags: #transitions[prevtag]:
            transitions[prevtag][tag] = (transitions[prevtag][tag]+1.)/(tagcounts[prevtag]+len(tags))
            #transitions[prevtag][tag] *= 1./tagcounts[prevtag]

    for tag in emissions.keys():
        for word in words: #emissions[tag]:
            emissions[tag][word] = (emissions[tag][word]+1.)/(tagcounts[tag]+len(wordcounts))
            #emissions[tag][word] *= 1./tagcounts[tag]

    #print len(transitions), len(emissions), len(tagcounts)
    return (transitions, emissions, tags)

def strip_tags(tagged_sentences):
    """Given a list of tagged sentences, return a list of untagged sentences"""
    untagged_sentences = []
    for taggedsent in tagged_sentences:
        untaggedsent = ''
	for taggedword in taggedsent.split():
	    word = re.split('(?<!\\\)\/', taggedword)[0]
            untaggedsent += word + ' '
        #print untaggedsent
        untagged_sentences.append(untaggedsent)
    return untagged_sentences

def maxsequence(probtable, tags):
    """Given a filled Viterbi probabibility table, return the most likely 
    sequence of POS tags"""
    r = len(probtable)
    c = len(probtable[0])

    maxfinalprob = 0
    maxfinaltag = None
    for i in range(r):
        if (probtable[i][c-1][0] > maxfinalprob):
            maxfinalprob = probtable[i][c-1][0]
            maxfinaltag = i

    #print maxfinaltag

    maxsequence = []
    prevmaxtag = maxfinaltag
    for j in range(c-1, -1, -1):
        maxsequence.insert(0, tags[prevmaxtag])
        #print probtable[prevmaxtag][j][1]
        prevmaxtag = probtable[prevmaxtag][j][1]
	    
    return maxsequence

def viterbi_tags (untagged_sentences, h):
    """Given a list of untagged sentences, return the most likely sequence of
    POS tags"""
    transitions = h[0]
    emissions = h[1]
    tags = h[2]
    maxtags = []
    #print tags

    for untaggedsent in untagged_sentences:
        #Create empty probtable
        words = untaggedsent.split()
        r = len(tags)
        c = len(words)
        probtable = [None]*r
        for i in range(r):
            probtable[i] = [None]*c
            for j in range(c):
                probtable[i][j] = [None]*2

        #Initialize zeroth column of probtable
        prevtag = '<START>'
        word = words[0]
        for i in range(r):
            tag = tags[i]

            transition = transitions[prevtag][tag]
            if word in emissions[tag]:
                emission = emissions[tag][word]
            else:
                emission = .0001*emissions[tag]['<UNKNOWN>']

            probtable[i][0][0] = transition*emission
        
        #Fill in probtable
        for j in range(1, c):
            word = words[j]
            for i in range(r):
                tag = tags[i]
                maxprob = 0
                maxtag = None

                if word in emissions[tag]:
                    emission = emissions[tag][word]
                else:
                    emission = .0001*emissions[tag]['<UNKNOWN>']

                for k in range(r):
                    prevtag = tags[k]
                    transition = transitions[prevtag][tag]
                    prob = probtable[k][j-1][0]*transition*emission
                    
                    if (prob > maxprob):
                        maxprob = prob
                        maxtag = k

                probtable[i][j][0] = maxprob
                probtable[i][j][1] = maxtag

        #Find most likely sequence of POS tags of this sentence
        sentmaxtags = maxsequence(probtable, tags)
        maxtags.extend(sentmaxtags)

    #Return most likely sequence of POS tags of all sentences
    return maxtags

def true_tags (tagged_sentences):
    """Given a list of tagged sentences, return the tag sequence"""
    tags = []
    for sent in tagged_sentences:
        tags.extend([re.split('(?<!\\\)\/', word)[1] for word in sent.split()])
    return tags

def compare(mytags, truetags, reducedtagset):
    #print mytags, truetags
    score = 0
    length = len(mytags)
    for i in range(length):
	truetag = truetags[i]
	if reducedtagset:
            if re.match('VB', truetag) is not None: truetag = 'VB'
            elif re.match('NN', truetag) is not None: truetag = 'NN'
            elif re.match('JJ', truetag) is not None: truetag = 'JJ'
            elif re.match('RB', truetag) is not None: truetag = 'RB'

        if mytags[i] == truetag: score += 1
    
    return 1.*score/length

if __name__ == '__main__':
    f = open('wsj15-18.pos').readlines()
    
    #90% of data is used for training
    print '90% of data is used for training'
    print '--------------------------------'
    i = int(len(f)*.9)
    h = hmm(f[:i], False)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, False)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, False)
    print c2

    #70% is used for training
    print '70% of data is used for training'
    print '--------------------------------'
    j = int(len(f)*.7)
    h = hmm(f[:j], False)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, False)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, False)
    print c2

    #50% is used for training
    print '50% of data is used for training'
    print '--------------------------------'
    k = int(len(f)*.5)
    h = hmm(f[:k], False)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, False)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, False)
    print c2

    #30% is used for training
    print '30% of data is used for training'
    print '--------------------------------'
    l = int(len(f)*.3)
    h = hmm(f[:l], False)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, False)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, False)
    print c2
    
    #Reduced tagset, 90% is used for training
    print '90% of data is used for training, reduced tagset'
    print '------------------------------------------------'
    #i = int(len(f)*.9)
    h = hmm(f[:i], True)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, True)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, True)
    print c2
    
    #Reduced tagset, 70% is used for training
    print '70% of data is used for training, reduced tagset'
    print '------------------------------------------------'
    j = int(len(f)*.7)
    h = hmm(f[:j], True)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, True)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, True)
    print c2

    #Reduced tagset, 50% is used for training
    print '50% of data is used for training, reduced tagset'
    print '------------------------------------------------'
    k = int(len(f)*.5)
    h = hmm(f[:k], True)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, True)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, True)
    print c2

    #Reduced tagset, 30% is used for training
    print '30% of data is used for training, reduced tagset'
    print '------------------------------------------------'
    l = int(len(f)*.3)
    h = hmm(f[:l], True)

    test1 = f[i:]
    v1 = viterbi_tags(strip_tags(test1), h)
    t1 = true_tags(test1)
    c1 = compare(v1, t1, True)
    print c1

    test2 = open('wsj_0159.pos').readlines()
    v2 = viterbi_tags(strip_tags(test2), h)
    t2 = true_tags(test2)
    c2 = compare(v2, t2, True)
    print c2
