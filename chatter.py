#!/usr/bin/python

import re, random, bisect, argparse

def increment_key(key, subkey, dictionary):
    if key not in dictionary:
        dictionary[key] = {}
    if subkey not in dictionary[key]:
        dictionary[key][subkey] = 1
    else:
        dictionary[key][subkey] += 1
        
def select_weighted(dictionary):
    items, total = [], 0
    for key, value in dictionary.items():
        total += value
        items.append((total, key))
    return items[bisect.bisect_left(items, (random.randint(1, total),))][1]

class Chatter:

    def __init__(self):
        self.chars = {}
        self.words = {}
        self.avg_word_length = 0
        self.avg_sentence_length = 0
        self.delims = ['!','?','.',]

    def learn(self, file):
        text = file.read()

        print 'learning ' + file.name
        text = text.lower()
        sentences = re.split(r'\s*[!?.,;:]\s*', text)
        for sentence in sentences:
            word_list = sentence.split()
            
            # skip if there's nothing to do
            if not word_list:
                continue
            
            # store the beginning of sentences with key None
            increment_key(None, word_list[0], self.words)
            for i, word in enumerate(word_list):                
                # build frequency distribution of followers for words (again follower is None if it is the last word in sentence)
                if i < len(word_list) - 1:
                    follow_word = word_list[i + 1]
                else:
                    follow_word = None
                increment_key(word, follow_word, self.words)
                
                # build frequency distribution of followers for single chars
                char_list = list(word)
                # add entry for the start of words - key None
                increment_key(None, char_list[0], self.chars)
                # add entries for the rest of chars in the word, includes a marker for the end (value: None)
                for j, char in enumerate(char_list):    
                    if j < len(char_list) - 1:
                        follower = char_list[j + 1]
                    else:
                        follower = None
                    increment_key(char, follower, self.chars)
                

    def gibber(self):
        print '\ngibber:'
        char = select_weighted(self.chars[None])
        word = ''
        word += char
        for i in range(1, 10):
            char = select_weighted(self.chars[char])
            if char == None:
                break
            word += char
        print word

    def babbel(self):
        print '\nbabbel:'
        word = select_weighted(self.words[None])
        sentence = []
        sentence.append(word)
        for i in range(1, 10):
            word = select_weighted(self.words[word])
            if word == None:
                break
            sentence.append(word)
        sentence = ' '.join(sentence)
        print sentence + random.choice(self.delims)
        
    def dump_memory():
        self.dump_chars()
        self.dump_words()
        
    def dump_chars():
        print 'dump chars'
        
    def dump_words():
        print 'dump words'
        
    

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate random sentences and words from specified input files.')
    parser.add_argument('files', metavar='FILE', type=argparse.FileType('r'), nargs='*', 
            default=open('sample_data/Goethe_Werther.txt', 'r'), help='A text file containing input data')
    args = parser.parse_args()
    files = args.files

    if not type(files) is list:
        files = [files]

    c = Chatter()
    for file in files:
        c.learn(file)
    c.babbel()
    c.gibber()
    
