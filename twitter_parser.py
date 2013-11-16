import os
import lxml.html
import nltk, re, pprint 

#nltk.download()            # install packages
os.chdir("C:/Users/Logan/Desktop")      # sets work directory

rawtext = open("1.crf").read() 
#print rawtext               # prints rawtext

"""list of lists of tuples.
   Python code for segmentation, tokenization, and POS tagging"""

def ie_preprocess(document):     
    """This function takes raw text and chops and then connects the process to break     
       it down into sentences, then words and then complete part-of-speech tagging"""
    sentences = nltk.sent_tokenize(document)  #NLTK default sentence segmenter
    #print sentences   # sentences are segmented
    sentences = [nltk.word_tokenize(sent) for sent in sentences] # NLTK word tokenizer 
    #print sentences   # sentences are tokenized
    sentences = [nltk.pos_tag(sent) for sent in sentences] # NLTK POS tagger 
    #print sentences   # sentences are POS tagged
    return sentences

#import xml
base_url = "http://www.stokesentinel.co.uk/Yobs-pelt-999-crews-bottles-fireworks-Shelton/story-17256383-detail/story.html"
page = lxml.html.parse(base_url)
story = page.xpath('//*[@id="main-article"]') # Use firebug you silly goose
raw_text = story[0].text_content()
#tokenize  
output = ie_preprocess(raw_text)
#print output

#chunking
grammar = r'''
   NP: 
   {<DT><NN.*><.*>*<NN.*>} 
   '''
cp = nltk.RegexpParser(grammar)
chunked = []
for s in output:
    chunked.append(cp.parse(s))
print chunked       #assume this is training


# get training and testing data
from nltk.corpus import conll2000
grammar = r"NP: {<[CDJNP].*>+}"
cp = nltk.RegexpParser(grammar)
test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
#print test_sents
#print cp.evaluate(test_sents)
#train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
#print train_sents
#print cp.evaluate(train_sents)


# Natural Language Toolkit: code_unigram_chunker

class UnigramChunker(nltk.ChunkParserI):
    #def __init__(self, train_sents):
    def __init__(self, chunked): # [_code-unigram-chunker-constructor]
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)]
                      for sent in chunked]
        self.tagger = nltk.UnigramTagger(train_data) # [_code-unigram-chunker-buildit]

    def parse(self, sentence): # [_code-unigram-chunker-parse]
        pos_tags = [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.util.conlltags2tree(conlltags)

unigram_chunker = UnigramChunker(chunked)
print unigram_chunker.evaluate(test_sents)

# 1. create a chunk parser by defining patterns of NP chunks or using the trained one 
class ChunkParser(nltk.ChunkParserI): 
    #def __init__(self, train_sents): 
            #train_data = [[(t,c) for w,t,c in nltk.chunk.util.tree2conlltags(sent)] for sent in train_sents] 
    def __init__(self, chunked): 
            train_data = [[(t,c) for w,t,c in nltk.chunk.util.tree2conlltags(sent)] for sent in chunked] 
            self.tagger = nltk.TrigramTagger(train_data)

# 2. parse every sentence
    def parse(self, sentence):
        pos_tags = [pos for (word,pos) in sentence] 
        tagged_pos_tags = self.tagger.tag(pos_tags) 
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags] 
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag) in zip(sentence, chunktags)] 
        # TODO: Do not use string as intermediate for parsing
        #conllstr = '\n'.join([' '.join([w, p, c if c else 'O']) for (w,p,c) in conlltags])
        return nltk.chunk.util.conlltags2tree(conlltags)

    def parse_draw(self, sentence):
        trees = parse(self, sentence)
        nltk.draw.draw_trees(*trees)

    def parse_print(self, sentence):
        trees = parse(self, sentence)
        for tree in trees:
            print tree

# 3. store NP chunks
    def npchunk_features(sentence, i, history):
         word, pos = sentence[i]
         if i == 0:
             prevword, prevpos = "<START>", "<START>"
         else:
             prevword, prevpos = sentence[i-1]
         if i == len(sentence)-1:
             nextword, nextpos = "<END>", "<END>"
         else:
             nextword, nextpos = sentence[i+1]
         return {"pos": pos,
                 "word": word,
                 "prevpos": prevpos,
                 "nextpos": nextpos,
                 "prevpos+pos": "%s+%s" % (prevpos, pos),
                 "pos+nextpos": "%s+%s" % (pos, nextpos),
                 "tags-since-dt": tags_since_dt(sentence, i)}

 	
    def tags_since_dt(sentence, i):
         tags = set()
         for word, pos in sentence[:i]:
             if pos == 'DT':
                 tags = set()
             else:
                 tags.add(pos)
         return '+'.join(sorted(tags))

chunker = ChunkParser(chunked)
print chunker.evaluate(test_sents)

#keywords extraction
