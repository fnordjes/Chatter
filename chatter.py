#!/usr/bin/python2.7

import re, random, argparse

class Chatter(object):
    def __init__(self):
        self.chars = {}
        self.words = {}
        self.avg_word_length = 0
        self.avg_sentence_length = 0
        self.delims = ['!','?','.']

    def learn(self, text):
        text = text.lower()
        sentences = re.split(r'\s*["!?.,;:]\s*', text)
        for sentence in sentences:
            word_list = sentence.split()
            
            # skip if there's nothing to do
            if not word_list:
                continue
            
            # store the beginning of sentences with key None
            self.increment_key(None, word_list[0], self.words)
            for i, word in enumerate(word_list):                
                # build frequency distribution of followers for words (again
                # follower is None if it is the last word in sentence)
                follow_word = self.select_follower(i, word_list)
                self.increment_key(word, follow_word, self.words)
                
                # build frequency distribution of followers for single chars
                char_list = list(word)
                # add entry for the start of words - key None
                self.increment_key(None, char_list[0], self.chars)
                # add entries for the rest of chars in the word, includes a
                # marker for the end (value: None)
                for j, char in enumerate(char_list):
                    follower = self.select_follower(j, char_list)
                    self.increment_key(char, follower, self.chars)
                
    def gibber(self):
        char = self.select_weighted(self.chars[None])
        word = ''
        word += char
        for _ in range(1, 10):
            char = self.select_weighted(self.chars[char])
            if char == None:
                break
            word += char
        print word

    def babbel(self):
        word = self.select_weighted(self.words[None])
        sentence = []
        sentence.append(word)
        for _ in range(1, 10):
            word = self.select_weighted(self.words[word])
            if word == None:
                break
            sentence.append(word)
        sentence = ' '.join(sentence)
        print sentence + random.choice(self.delims)
        
    #def dump_memory(self):

        
    def dump_chars():
        print 'dump chars'
        
    def dump_words():
        print 'dump words'
        
    @staticmethod
    def select_follower(pos, item_list):
        if pos < len(item_list) - 1:
            follower = item_list[pos + 1]
        else:
            follower = None
        return follower
        
    @staticmethod
    def increment_key(key, subkey, dictionary):
        if key not in dictionary:
            dictionary[key] = {}
        if subkey not in dictionary[key]:
            dictionary[key][subkey] = 1
        else:
            dictionary[key][subkey] += 1
            
    @staticmethod
    def select_weighted(dictionary):
        random_pick = random.uniform(0, sum(dictionary.itervalues()))
        total = 0.0
        for key, value in dictionary.iteritems():
            total += value
            if random_pick < total: return key
        return key
        
    

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=
        'Generate random sentences and words from specified input files.')
    parser.add_argument('-i', metavar='INPUT FILE',
        type=argparse.FileType('r'),
        nargs='*', help='Text file(s) containing input data')
    parser.add_argument('-o', metavar='OUTPUT FILE',
        type=argparse.FileType('w'),
        help='Textfile to store what has been learned')
    parser.add_argument('-d', metavar='DICTIONARY FILE',
        type=argparse.FileType('r'),
        help='Restore dictionary from file')
    args = parser.parse_args()
    files = args.i

    if not type(files) is list:
        files = [files]

    c = Chatter()
    for file in files:
        c.learn(file.read())
        file.close()
    
    c.babbel()
    #c.gibber()
    
