#!/usr/bin/env python
# encoding: utf-8
#
# Code to align manual transcripts (MTR) and episode outline 
# (OL) represented in terms of Annotation Graphs.
#
# The MIT License (MIT)
# Copyright (c) 2014 Anindya Roy (http://roy-a.github.io/)
# 30.03.2014.
#
#
#
# This script uses NLTK. Reference for NLTK:
# Bird, Steven, Edward Loper and Ewan Klein (2009), 
# Natural Language Processing with Python. O’Reilly Media Inc.
#
#
# NB: HERVE: Pl. search "HERVE" inside this script to find where you
#     may need to make edits.
#
# NB: For installing nltk, do not use "pip install nltk" -> version issue.
#     Use "easy_install nltk" - this gets over version issue.
# NB: Also MUST install nltk_data:
#     python -m nltk.downloader all
#
#
#
#
# NB: Some episodes with no OL (ALREADY REMOVED from yml file):
#     2_21, 3_22, 4_8, 4_10, 4_12 and all following episodes.
#
# NB: Better way to align would be to consider speaker names & dialogue separately
#       as was done for the IR experiments (leading to improved performance).
#       Here, we follow what was reported in LREC 2014 paper.
#
#=================================================================================



from tvd import AnnotationGraph
from tvd import TStart, TFloating, TEnd, Episode
import os, glob 

import sys, re, math, unicodedata
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.corpus import wordnet as wn
import numpy as np

stopwords = nltk.corpus.stopwords.words('english')


# Folder path for 'www' resources.
#---------------------------------
# HERVE -> Pl. edit accordingly.
wwwdir = '/tmp/TheBigBangTheory/www/' 
# Folder for MTR JSON files, should exist.
MTRdir = wwwdir + 'manual_transcript/'
# Folder for OL JSON files, should exist.
OLdir = wwwdir + 'outline/'
# Folder to write output aligned (MTR+OL) JSON files.
# This script will create this folder if needed.
aligndir = wwwdir + '/aligned/' 
series = 'TheBigBangTheory'
#----------------------------------------


# Global variable declarations.
# Optimal defaults: better not to change.
#----------------------------------------

# use_scenes = 0 # Do not use scene location info.
# use_scenes = 1 # Use scene location info AND
         # treat scene location nodes exactly
         # the same as other nodes.
use_scenes = 2 # Use scene location info BUT
           # weight similarity score between scene location and non-
           # non-scene location nodes differently than between
           # 2 scene or non-scene locatio nodes (as in LREC14 paper).
           # This option performs the best. 
    
do_wnet = 1 # Use WordNet similarity.
gamma = 0.0025 # WordNet weighting factor for non-scene location units.
gamma_scenes = 0.2 # WordNet weighting factor for scene locations.
maxsynsets = 1 # No. of synsets considered when calculating
           # WordNet similarity.

do_smoothing = 1 # Temporal smoothing using context window.
support_smoothing = [-1, 0]
weights_smoothing = {-1:1.0, 0:1.25}

chars = ['.', '/', "'", '"', '\?', '\!', '#', '$', '%', '^', '&',
            '\*', '\(', '\)', ' - ', '_', '\+' ,'=', '@', ':', ',',
            ';', '~', '`', '<', '>', '|', '\[', '\]', '{', '}', '–', '“',
            '»', '«', '°', '’', '…', '\xe2\x80\xa8', '\xe2\x80\xa6']
#-------------------------------------------------------------------------


# Function definitions.
#----------------------

def graph2text(jsonFile): 

    """This function reads in an AnnotationGraph from a JSON
    file 'jsonFile' and returns its content in an intermediate
    text format suitable for alignment later. 

    The graph MUST correspond to either an MTR or OL track.

    Parameters
        ----------
        jsonfile : str
            name of file in JSON format containing the graph.

        Returns
        -------
        success : [1, 0]
    words : list of text elements
        Each element is a unit (e.g. dialogue line, event/scene location)
        to be aligned.
    isScene : list of integer elements
        1 if corresponding element of 'words' is a scene location, 
        0 otherwise.

    """
    G = AnnotationGraph.load(jsonFile)
    words = []
    isScene = [] # set to 1 if scene location, 0 if not.
    success = 1

    start = TStart()
    current_node = start
    next_node_exists = 0
    while 1:

        next_nodes = G[current_node].keys()
        if not next_nodes: # End of graph.
            break
        
        for node in next_nodes:

            # IMP: Assume single edge between 2 nodes.
            edge = G[current_node][node][0] 

            # Check if it is a 'location' branch.
            if 'location' in edge: 

                words.append(edge['location'])
                isScene.append(1)
                next_location_node = node # Save this node.
                              # -> use iff no other next nodes exist.
            else:
                # Main (non-location) branch.
                next_node = node
                next_node_exists = 1
                if edge:

                    text = []
                    for item in edge: # 'speaker', 'speech', 'event'.

                        text.append(edge[item])

                    text = ' '.join(text)
                    words.append(text)
                    isScene.append(0)

        if next_node_exists == 0: # Next node was not found.
            next_node = next_location_node 
                # Set next node as the next location node.          
                # Assume at least one location node exists in graph.
        current_node = next_node
        next_node_exists = 0
    if len(words) <= 2: # Check if at least 2 nodes exist.
        success = 0 # If not, data is probably corrupted/empty. (Heuristic)
        words = []  
        isScene = []
    return (success, words, isScene)
#-------------------------------------------------------------------------------------

def list_of_graphs2text(jsonFilelist):
    """ Processes a list of json files each containing an
    Annotation Graph, and returns the whole data in an 
    intermediate text format for alignment later.

    Parameters:
    -----------
    jsonfilelist : list of str
        Each element is the name of a JSON file containing
        one annotation graph.

    Returns:
    --------
    success_, words_, isScene_ : concatenated output lists from
        graph2text
    idx : list of pairs of indices pointing to start and end of 
        graphs inside success_, words_ and isScene_.

    """
    
    isScene_ = [] # 1 if corresp. text is a scene location, 0 if not.
    words_ = [] # Processed sentences.
    success_ = []
    idx = []
    nSents = 0
    for filename in jsonFilelist:
        #print filename
        (success, words, isScene) = graph2text(filename)
        words_.extend(words)
        isScene_.extend(isScene)
        success_.append(success) 
        nSents_ = nSents + len(words)
        idx.append([nSents, nSents_])
        nSents = nSents_
        
    return (success_, words_, isScene_, idx)
#------------------------------------------------------------------

def get_common_episodes(list1, list2):
    # List of episodes/files with both MTR & OL available.
    list1_ = []
    list2_ = []

    dir1 = '/'.join(list1[0].split('/')[:-1])
    dir2 = '/'.join(list2[0].split('/')[:-1])
    for item in list1:
        basename = item.split('/')[-1]
        if (dir2 + '/' + basename) in list2:
            list1_.append(dir1 + '/' + basename)
            list2_.append(dir2 + '/' + basename)

    return (list1_, list2_)
#----------------------------------------------------------------

# Compute WordNet-based word similarities.
def sim(w1, w2):
    if wn.synsets(w1): # if it exists in WordNet.
        s1 = wn.synsets(w1)[0] 
    else:
        return 0
    if wn.synsets(w2):
        s2 = wn.synsets(w2)[0]
    else:
        return 0
    scores = wn.wup_similarity(s1,s2) # Faster.
    if scores:
        return scores
    else:
        return 0
#---------------------------------------------------------

# Word similarities using ALL synsets (slower, sub-optimal).
def sim2(w1, w2):
    if wn.synsets(w1): # if it exists in WordNet.
        s1 = wn.synsets(w1)[0:maxsynsets]
    else:
        return 0
    if wn.synsets(w2):
        s2 = wn.synsets(w2)[0:maxsynsets]
    else:
        return 0
    scores = []
    for s1_ in s1:
        for s2_ in s2:
            scores.append(wn.wup_similarity(s1_,s2_))
    if max(scores):
        return max(scores)
    else:
        return 0
#-------------------------------------------------------------

# DTW function to compute best path alignment.
# l = local objective function matrix. 
# l(event node ID,speech node ID) = (mapped) TFIDF score between event node & speech node.
def dtw(l):
    # DTW global obj function matrix.
    g = np.zeros_like(l)
    # Best path matrix.  
    bp = np.zeros_like(l)

    g[0][0] = l[0][0]

    for row in range(1,g.shape[0]):
        g[row][0] = g[row-1][0] + l[row][0]
        bp[row][0] = 2

    for col in range(1,g.shape[1]):
        g[0][col] = g[0][col-1] + l[0][col]
        bp[0][col] = 1


    for row in range(1,g.shape[0]):
        for col in range(1,g.shape[1]):
            bp[row][col] = 1 + np.argmax(np.array([-np.inf, g[row-1][col], g[row-1][col-1]]))
            g[row][col] = l[row][col] + np.amax(np.array([-np.inf, g[row-1][col], g[row-1][col-1]]))

    return (g,bp)
#-----------------------------------------------------------------------

# Function to tokenize and lemmatize text.
def tokenize(text):

    text = ' '.join(text)
    tokens = PunktWordTokenizer().tokenize(text)
    # Lemmatize words. try both noun and verb lemmatizations
    lmtzr = WordNetLemmatizer()
    for i in range(0,len(tokens)):
        res = lmtzr.lemmatize(tokens[i])
        if res == tokens[i]:
            tokens[i] = lmtzr.lemmatize(tokens[i], 'v')
        else:
            tokens[i] = res
    # Do not return any single letters
    tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
    
    return tokens
#------------------------------------------------------------------------

def remove_stopwords(text, stopwords1 = stopwords):
    # remove punctuation
    for c in chars:
        #text = text.replace(c, ' ')
        text = re.sub(c, ' ', text)
    text = text.split()
    content = [w for w in text if w.lower().strip() not in stopwords1]
    return content
#------------------------------------------------------------------------



# MAIN SCRIPT BODY.

# Make list of JSON graph files.
MTRlist = glob.glob(MTRdir + '*.json')
OLlist = glob.glob(OLdir + '*.json')
    
# List of episodes/files which have both MTR & OL.
(MTRlist, OLlist) = get_common_episodes(MTRlist, OLlist)
nFiles = len(OLlist)

(success1, words1, isScene1, idx1) = list_of_graphs2text(OLlist)
(success2, words2, isScene2, idx2) = list_of_graphs2text(MTRlist)

# NB: Successfully extracted MTR & OL from ALL 67 episodes in 
# current yml list successful. 


# Computing (Inverse) Document Frequencies for words over OL & MTR.
DF1 = {} 
IDF1 = {}
DF2 = {}
IDF2 = {}

# Processing OL text.
#-------------------
words_1 = [] 
for fileNo in xrange(nFiles):

    sents = words1[idx1[fileNo][0]:idx1[fileNo][1]]
    # Treat each sentence as 1 document. Nelken et al. 2006.
    for sent in sents:
        
        words = remove_stopwords(sent)
        words = tokenize(words)
        terms = {}

        for word in words:
            terms[word] = 1

        for (word,exists) in terms.items():

            if word in DF1:
                DF1[word] += 1
            else:
                DF1[word] = 1

        words_1.append(words)
        

nSents = len(words_1) # Total over all files.
for (word,df) in DF1.items():
    IDF1[word] = math.log(float(1 + nSents) / float(1 + DF1[word]))

# Processing MTR text
#---------------------
words_2 = [] # Processed sentences.
for fileNo in xrange(nFiles):
    
    sents = words2[idx2[fileNo][0]:idx2[fileNo][1]]
    # Treat each sentence as 1 document. Nelken et al. 2006.
    for sent in sents:
        
        words = remove_stopwords(sent)
        words = tokenize(words)
        terms = {}

        for word in words:
            terms[word] = 1

        for (word,exists) in terms.items():

            if word in DF2:
                DF2[word] += 1
            else:
                DF2[word] = 1

        words_2.append(words)
        
nSents = len(words_2)
for (word,df) in DF2.items():
    IDF2[word] = math.log(float(1 + nSents) / float(1 + DF2[word])) 


if not os.path.exists(aligndir):
    os.makedirs(aligndir)

# Alignment.
#-------------
#nFiles = 6
for fileNo in xrange(nFiles): 
    print "File no. " + str(fileNo + 1)
    print "==========="

    # Processed text for this episode.
    words_1_ = words_1[idx1[fileNo][0] : idx1[fileNo][1]]
    words_2_ = words_2[idx2[fileNo][0] : idx2[fileNo][1]]
    isScene1_ = isScene1[idx1[fileNo][0] : idx1[fileNo][1]]
    isScene2_ = isScene2[idx2[fileNo][0] : idx2[fileNo][1]]
    N1 = len(words_1_)
    N2 = len(words_2_)
    if N1 == 0 or N2 == 0:
        continue

    tfidf1 = [] # List of dictionaries, one for each sentence.
    for n1 in xrange(N1):
        # Calculate TFIDF for this sentence.
        tfidf = {}
        maxtf = -np.inf
        for word in words_1_[n1]:
            if word in tfidf:
                tfidf[word] += 1
            else:
                tfidf[word] = 1
            if tfidf[word] > maxtf:
                    maxtf = tfidf[word]
        norm = 0
        for (word,value) in tfidf.items():
            tfidf[word] = float(value) * float(IDF1[word]) / float(maxtf)
            norm += float(tfidf[word]) * float(tfidf[word])
        norm = math.sqrt(norm)
        for (word,value) in tfidf.items():
            tfidf[word] /= norm # Unit normalization.
            #if tfidf[word] > 0:
            #   tfidf[word] = 1 # Just 1/0 -> If want only word overlap.
        tfidf1.append(tfidf)
        
    tfidf2 = [] # List of dictionaries, one for each sentence.
    if do_smoothing == 0:
        for n2 in xrange(N2):
            # Calculate TFIDF for this sentence.
            tfidf = {}
            maxtf = -np.inf
            for word in words_2_[n2]:
                if word in tfidf:
                    tfidf[word] += 1
                else:
                    tfidf[word] = 1
                if tfidf[word] > maxtf:
                        maxtf = tfidf[word]
            norm = 0 # Unit norm.
            for (word,value) in tfidf.items():
                tfidf[word] = float(value) * float(IDF2[word]) / float(maxtf)
                norm += float(tfidf[word]) * float(tfidf[word])
            norm = math.sqrt(norm)
            for (word,value) in tfidf.items():
                tfidf[word] /= norm 
            tfidf2.append(tfidf)

    if do_smoothing == 1:
        for n2 in xrange(N2):
            # Calculate TFIDF for this sentence & its (smoothed) context.
            tfidf = {}
            maxtf = -np.inf
            if use_scenes == 2 and isScene2_[n2] == '1':
                support_smoothing_ = [0] # Scene lines should not use context.
            else:
                support_smoothing_ = support_smoothing
            for offset in support_smoothing_:
                if n2 + offset >= 0 and n2 + offset < N2:
                    for word in words_2_[n2 + offset]:
                        if word in tfidf:
                            tfidf[word] += weights_smoothing[offset]
                        else:
                            tfidf[word] = weights_smoothing[offset]
                        if tfidf[word] > maxtf:
                            maxtf = tfidf[word]
            norm = 0 # Unit norm.
            for (word,value) in tfidf.items():
                tfidf[word] = float(value) * float(IDF2[word]) / float(maxtf)
                norm += float(tfidf[word]) * float(tfidf[word])
            norm = math.sqrt(norm)
            for (word,value) in tfidf.items():
                tfidf[word] /= norm 
            tfidf2.append(tfidf)
    
    # Calculate Cosine distance.
    l = np.zeros([N2, N1])  
    for n1 in xrange(N1):
        for n2 in xrange(n1,N2):
            for (word1, value1) in tfidf1[n1].items():
                for (word2, value2) in tfidf2[n2].items():
                    if word1 == word2:
                        l[n2][n1] += float(tfidf1[n1][word1]) * float(tfidf2[n2][word2]) 
                        # Inner product of unit vectors.
                    elif do_wnet:
                        if (
                            use_scenes == 2 and 
                            isScene1_[n1] == '1' and 
                            isScene2_[n2] == '1'
                        ):
                            l[n2][n1] += gamma_scenes * float(tfidf1[n1][word1]) * float(tfidf2[n2][word2]) * sim(word1, word2)
                        #else                       
                        #   l[n2][n1] += gamma *
                        #       float(tfidf1[n1][word1]) *
                        #       float(tfidf2[n2][word2]) *
                        #       sim(word1, word2)   
                            # Not useful (LREC14).  
            if use_scenes == 2:
                if isScene1_[n1] == '1' and isScene2_[n2] == '1':
                    l[n2][n1] *= 1.2
                if isScene1_[n1] != isScene2_[n2]:
                    l[n2][n1] *= 0.1
                        

    # Transforming into probs by passing through a sigmoid.
    if 1:
        # prior = float(1.0/N1) # Prior probability of getting aligned.
        # Sort l.
        l_ = np.sort(l, axis = None) # Ascending.
        # Find the element which is at prior position.
        theta = l_[N2*N1 - 1.0*N2]
        # Set slope.
        b = -1.5 # Could calculate it by assuming sum of probs
             # over one speech node is equal to 1.
        # Calculate offset.
        a = -b*theta            
        for n1 in xrange(N1):
            for n2 in xrange(N2):
                l[n2][n1] = math.log(1 / (1 + math.exp(a + b*float(l[n2][n1])))) 

    # DTW step.
    (g,bp) = dtw(l)

    # Just need to backtrack and find the changeover points.
    # n1: event, col, n2: speech, row.
    n2_ = N2 - 1
    n1_ = N1 - 1
    x = np.zeros_like(l)
    while (n1_ >= 0) and (n2_ >= 0) :
        x[n2_][n1_] = 1
        if bp[n2_][n1_] == 3:
            n2_ -= 1
            n1_ -= 1
        else:
            n2_ -= 1

    N1 = np.shape(x)[1]
    N2 = np.shape(x)[0]
    
    # Create graph with aligned MTR & OL.
    rm = re.search('\.Season(?P<season>\d{2})\.Episode(?P<episode>\d{2})\.json', 
            OLlist[fileNo])
    episodeNo = rm.group('episode')
    seasonNo = rm.group('season')
    episode = Episode(series, seasonNo, episodeNo)
    G = AnnotationGraph(episode=episode)
    
    # Raw text for this episode.
    words1_ = words1[idx1[fileNo][0] : idx1[fileNo][1]]
    words2_ = words2[idx2[fileNo][0] : idx2[fileNo][1]]
    N1 = len(words1_)
    N2 = len(words2_)

    t_episode_start = TStart()
        t_episode_stop = TEnd()
        t_location_prev = t_episode_start
        t_event_prev = None
    t_speech_prev = None

    for n1 in xrange(N1):

        if isScene1_[n1] == 1: # Scene location node.

            if t_event_prev:
                            G.add_annotation(t_event_prev, t_location_prev, {}) 
            t_location_start = TFloating()
                    G.add_annotation(t_location_prev, t_location_start, {})
                    t_location_stop = TFloating()
                    G.add_annotation(
                        t_location_start, t_location_stop,
                            {'location': words1_[n1]}
                    )
                    t_location_prev = t_location_stop
                    t_event_prev = t_location_start

        else: # Event node.
            
            t_event_start = TFloating()
                        t_event_stop = TFloating()
                        G.add_annotation(t_event_prev, t_event_start, {})
                        G.add_annotation(
                            t_event_start, t_event_stop,
                            {'event': words1_[n1]}
                        )
                        t_event_prev = t_event_stop
            t_speech_prev = t_event_start

            # Add all speech (dialogue) nodes (from MTR) corresponding
            # to this event node (in OL) between start and stop nodes
            # for this event.

            for n2 in xrange(N2):
                if x[n2][n1] == 1: # i.e. this speech node 
                           # corresponds to the current event.
                    speaker = re.match('\A\s*[^:\.]+\s*:', words2_[n2])
                    if not speaker:
                        continue
                    speaker = speaker.group()
                    speech = re.sub('\A\s*[^:\.]+\s*:\s*', '', words2_[n2])
                
                    t_speech_start = TFloating()
                    t_speech_stop = TFloating()
                    G.add_annotation(t_speech_prev, t_speech_start, {})
                    G.add_annotation(
                        t_speech_start, t_speech_stop,
                        {'speaker' : speaker, 'speech' : speech}
                    )
                    t_speech_prev = t_speech_stop

            G.add_annotation(t_speech_prev, t_event_prev, {})

        G.add_annotation(t_event_prev, t_location_prev, {})

    G.add_annotation(t_location_prev, t_episode_stop, {})
    basename = OLlist[fileNo].split('/')[-1]
    G.save(aligndir + basename)
                
    

    
    
