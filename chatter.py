#!/usr/bin/python2.7

import re, random, argparse, ast, sys, os.path

class Chatter(object):
    def __init__(self):
        self.chars = {}
        self.words = {}
        
        self.stats = {}
        # words per sentence stats
        self.stats['words'] = {}
        self.stats['words']['count'] = 0.0
        self.stats['words']['avg'] = 0.0

        # chars per word stats        
        self.stats['chars'] = {}
        self.stats['chars']['count'] = 0.0
        self.stats['chars']['avg'] = 0.0
        
        # todo: here we have fixed propabilities for sentence delimiters
        self.delims = {'!': 1, '?': 2, '.': 7}

    def learn(self, text):
        text = text.lower()
        sentences = re.split(r'\s*[()"!?.,;:]+\s*', text)
        for sentence in sentences:
            word_list = re.findall(r'[\w\d]+[\-\']{0,1}[\w\d]+|[\w\d]+', sentence)

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
                if not char_list:
                    continue

                # add entry for the start of words - key None
                self.increment_key(None, char_list[0], self.chars)
                # add entries for the rest of chars in the word, includes a
                # marker for the end (value: None)
                for j, char in enumerate(char_list):
                    follower = self.select_follower(j, char_list)
                    self.increment_key(char, follower, self.chars)
                    self.stats['chars']
                self.__update_average(j + 1, self.stats['chars'])

            self.__update_average(i + 1, self.stats['words'])
            
    def gibber(self):
        # todo: we define a max length for the sentence as avg_length + 50%
        avg = self.stats['words']['avg']
        n = int(random.uniform(avg, avg * 1.5))
        sentence = []
        for _ in range (0, n):
            sentence.append(self.create_word())
        sentence = ' '.join(sentence)
        return sentence + self.select_weighted(self.delims)

    def babbel(self, about=None):
        # todo: we define a max length for the sentence as avg_length + 50%
        avg = self.stats['words']['avg']
        n = int(random.uniform(avg, avg * 1.5))
        sentence = []
        
        # beginning with the string 'about' create the start of the sentence
        # (climb up the chain of words until a starter is found)
        if about and about in self.words:
            word = about
            while word != None:
                sentence.insert(0, word)
                word = self.select_weighted(self.words[word]['asc'])
            word = about    
        else:
            word = self.select_weighted(self.words[None]['dsc'])
            
        # build (the rest of) the sentence climbing the chain down
        for _ in range(0, n):
            word = self.select_weighted(self.words[word]['dsc'])
            if word == None:
                break
            sentence.append(word)
        sentence = ' '.join(sentence)
        return sentence + self.select_weighted(self.delims)
        
    def create_word(self):
        # todo: we define a max length for the word as avg_length + 50%
        avg = self.stats['chars']['avg']
        n = int(random.uniform(avg, avg * 1.5))
        char = self.select_weighted(self.chars[None]['dsc'])
        word = ''
        word += char
        for _ in range(0, n):
            char = self.select_weighted(self.chars[char]['dsc'])
            if char == None:
                break
            word += char
        return word
        
    def dump_memory(self):
        return {
            'chars': self.chars,
            'words': self.words,
            'stats': self.stats
        }
        
    def read_dict(self, dictionary):
        self.chars = dictionary['chars']
        self.words = dictionary['words']
        self.stats = dictionary['stats']

    def __update_average(self, count, stats):
        stats['count'] += 1
        stats['avg'] += (float(count) - stats['avg']) / float(stats['count'])
        
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
            dictionary[key]['asc'] = {}
            dictionary[key]['dsc'] = {}
        if subkey not in dictionary:
            dictionary[subkey] = {}
            dictionary[subkey]['asc'] = {}
            dictionary[subkey]['dsc'] = {}
        
        # create link between words in descending order to be able to create
        # sentences from start to end
        if subkey not in dictionary[key]['dsc']:
            dictionary[key]['dsc'][subkey] = 1
        else:
            dictionary[key]['dsc'][subkey] += 1
        # create link between words in ascending order to bee able to create
        # sentences from back to start
        if key not in dictionary[subkey]['asc']:
            dictionary[subkey]['asc'][key] = 1
        else:
            dictionary[subkey]['asc'][key] += 1
            
    @staticmethod
    def select_weighted(dictionary):
        random_pick = random.uniform(0, sum(dictionary.itervalues()))
        total = 0.0
        for key, value in dictionary.iteritems():
            total += value
            if random_pick < total: return key
        return key
        
if __name__ == '__main__':
    # helper function to allow reading from and writing to file
    # and to create it in case it doesn't exist
    # argparse with type 'r+' doesn't create the file
    # directly opening with type 'w' creates a file but flushes its contents.
    def is_valid_file(parser, arg):
        if not os.path.exists(arg):
           f = open(arg, 'w')
           f.close
        return open(arg,'r')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=
        'Generate random sentences and words from specified input files.')
    parser.add_argument('-i', '--input', metavar='FILE',
        type=argparse.FileType('r'), nargs='*',
        help='Text file(s) containing input data (defaults to stdin)', 
        default=sys.stdin)
    parser.add_argument('-d', '--dict', metavar='FILE',
        type=lambda x: is_valid_file(parser,x),
        help='Restore and extend dictionary in file')
    parser.add_argument('-o', '--output', metavar='FILE',
        type=argparse.FileType('w'),
        help='Output of the babbelbot (defaults to stdout)',
        default=sys.stdout)
    parser.add_argument('-a', '--about', metavar='STRING',
        help='Give a word that should be included in the generated text')
    parser.add_argument('-l', '--length', metavar='INT',
        help='Number of sentences to generate (length may vary) default: 1',
        default=1)
    parser.add_argument('-g', '--gibber', action='store_true',
        help='Create gibberish, make up the words')
    args = parser.parse_args()
    in_files = args.input
    dict_file = args.dict
    out_file = args.output
    length = int(args.length)
    about = args.about

    c = Chatter()
    
    # restore memory
    if dict_file:
        s = dict_file.read()
        dict_file.close()
        if not s == "":
            try:
                s = ast.literal_eval(s)
                c.read_dict(s)
            except SyntaxError:
                sys.stderr.write('Cannot read dict file. Exiting.\n')
                sys.stderr.flush()
                exit(1)
    
    # consume input
    if in_files:
        if not type(in_files) is list:
            in_files = [in_files]
        for file in in_files:
            c.learn(file.read())
            file.close()
       
    # now lets babbel a bit
    for _ in range(0, length):
        if args.gibber:
            out_file.write(c.gibber() + ' ')
        else:
            out_file.write(c.babbel(about) + ' ')
        out_file.write('\n')
            
    # spit out what has been learned
    if dict_file:
        f = open(dict_file.name, 'w')
        f.write(str(c.dump_memory()))
        f.close()
    
    exit(0)
