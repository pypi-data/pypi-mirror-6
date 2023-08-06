import networkx as nx
from tvd import AnnotationGraph, TFloating
from tvd import GameOfThrones
import numpy as np
from tvd.algorithms.alignment import dtw

import nltk
stopwords = set(nltk.corpus.stopwords.words('english'))
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()


gameOfThrones = GameOfThrones('/tmp/')
episode = gameOfThrones.episodes[0]
outline = AnnotationGraph.load(
    gameOfThrones.path_to_resource(episode, 'outline'))
transcript = AnnotationGraph.load(
    gameOfThrones.path_to_resource(episode, 'manual_transcript'))

# make sure floating times are disjoint
TFloating.reset()
outline, omapping = outline.relabel_floating_nodes(mapping=None)
transcript, tmapping = transcript.relabel_floating_nodes(mapping=None)

oindex = [
    (t1, t2) 
    for (t1, t2, data) in outline.ordered_edges_iter(data=True) 
    if 'scene' in data]
tindex = [
    (t1, t2) 
    for (t1, t2, data) in transcript.ordered_edges_iter(data=True) 
    if 'speech' in data]


# raw text
oraw = {
    (t1, t2): outline[t1][t2][0]['scene'] for t1, t2 in oindex
}
traw = {
    (t1, t2): transcript[t1][t2][0]['speech'] for t1, t2 in tindex    
}

# tokenized, lower-cased text
otoken = {
    (t1, t2): [word.lower() for word in nltk.wordpunct_tokenize(oraw[t1, t2])] for t1, t2 in oindex
}

ttoken = {
    (t1, t2): [word.lower() for word in nltk.wordpunct_tokenize(traw[t1, t2])] for t1, t2 in tindex
}

# pos-tagged text
opos = {
    (t1, t2): nltk.pos_tag(otoken[t1, t2]) for t1, t2 in oindex    
}

tpos = {
    (t1, t2): nltk.pos_tag(ttoken[t1, t2]) for t1, t2 in tindex    
}

# lemmatize nouns, adjectives, adverbs and non-modal verbs
from nltk.corpus.reader.wordnet import ADJ, NOUN, ADV, VERB
keep = {
    'JJ': ADJ,
    'JJR': ADJ,
    'JJS': ADJ, 
    'NN': NOUN,
    'NNP': NOUN,
    'NNPS': NOUN,
    'NNS': NOUN,
    'RB': ADV,
    'RBR': ADV,
    'RBS': ADV,
    'VB': VERB,
    'VBD': VERB,
    'VBG': VERB,
    'VBN': VERB,
    'VBP': VERB,
    'VBZ': VERB
}

olem = {
    (t1, t2): [
        wnl.lemmatize(word, pos=keep[pos]) 
        for word, pos in opos[t1, t2] if pos in keep
    ] 
    for t1, t2 in oindex
}

tlem = {
    (t1, t2): [
        wnl.lemmatize(word, pos=keep[pos]) 
        for word, pos in tpos[t1, t2] if pos in keep
    ] 
    for t1, t2 in tindex
}

# remove stopwords
oset = {
    (t1, t2): set(olem[t1, t2]) - stopwords
    for t1, t2 in oindex
}

tset = {
    (t1, t2): set(tlem[t1, t2]) - stopwords
    for t1, t2 in tindex
}


T = len(tindex)
O = len(oindex)

def costFn(o, t):
    scene = oset[o]
    speech = tset[t]
    if len(speech) > 0:
        return 1.-float(len(scene & speech)) / len(speech)
    else:
        return 1.


x = np.zeros((O, T))
for o, (t1, t2) in enumerate(oindex):
    for t, (ta, tb) in enumerate(tindex):
        x[o, t] = costFn((t1, t2), (ta, tb))


_, path = dtw.dtw(oindex, tindex, costFn)

g = nx.compose(outline, transcript)

prev_o = None
for o, t in path:
    t1, t2 = oindex[o]
    ta, tb = tindex[t]
    if o != prev_o:
        g.pre_align(t1, ta, TFloating())
        prev_o = o
        print "\n", t1, "-->", t2, outline[t1][t2][0]['scene']
    print "--", ta, "-->", tb, transcript[ta][tb][0]['speaker'], transcript[ta][tb][0]['speech']




