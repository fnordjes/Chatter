#!/usr/bin/env python3

import re, random, argparse, json, sys, os.path

# marks the start and the end of sentences and words (json has no None keys)
EDGE = ''

def decode(data):
    # most texts are utf-8 nowadays, old ones often latin-1
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')

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
        # commas don't end a sentence, so they're not split on
        sentences = re.split(r'\s*[()"!?.;:]+\s*', text)
        for sentence in sentences:
            word_list = re.findall(r'[\w\d]+[\-\']{0,1}[\w\d]+|[\w\d]+', sentence)

            # skip if there's nothing to do
            if not word_list:
                continue

            # store the beginning of sentences with key EDGE
            self.increment_key(EDGE, word_list[0], self.words)
            for i, word in enumerate(word_list):
                # build frequency distribution of followers for words (again
                # follower is EDGE if it is the last word in sentence)
                follow_word = self.select_follower(i, word_list)
                self.increment_key(word, follow_word, self.words)

                # build frequency distribution of followers for single chars
                char_list = list(word)

                # add entry for the start of words - key EDGE
                self.increment_key(EDGE, char_list[0], self.chars)
                # add entries for the rest of chars in the word, includes a
                # marker for the end (value: EDGE)
                for j, char in enumerate(char_list):
                    follower = self.select_follower(j, char_list)
                    self.increment_key(char, follower, self.chars)
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
        if about and about.lower() in self.words:
            word = about.lower()
            while word != EDGE:
                sentence.insert(0, word)
                word = self.select_weighted(self.words[word]['asc'])
            word = about.lower()
        else:
            word = self.select_weighted(self.words[EDGE]['dsc'])
            sentence.append(word)

        # build (the rest of) the sentence climbing the chain down
        for _ in range(0, n):
            word = self.select_weighted(self.words[word]['dsc'])
            if word == EDGE:
                break
            sentence.append(word)
        sentence = ' '.join(sentence)
        return sentence + self.select_weighted(self.delims)

    def create_word(self):
        # todo: we define a max length for the word as avg_length + 50%
        avg = self.stats['chars']['avg']
        n = int(random.uniform(avg, avg * 1.5))
        char = self.select_weighted(self.chars[EDGE]['dsc'])
        word = ''
        word += char
        for _ in range(0, n):
            char = self.select_weighted(self.chars[char]['dsc'])
            if char == EDGE:
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
            follower = EDGE
        return follower

    @staticmethod
    def increment_key(key, subkey, dictionary):
        if key not in dictionary:
            dictionary[key] = {}
            dictionary[key]['asc'] = {}
            dictionary[key]['dsc'] = {}
            dictionary[key]['cnt'] = 0
        if subkey not in dictionary:
            dictionary[subkey] = {}
            dictionary[subkey]['asc'] = {}
            dictionary[subkey]['dsc'] = {}
            dictionary[subkey]['cnt'] = 0

        dictionary[key]['cnt'] += 1

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
        random_pick = random.uniform(0, sum(dictionary.values()))
        total = 0.0
        for key, value in dictionary.items():
            total += value
            if random_pick < total: return key
        return key

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=
        'Generate random sentences and words from specified input files.')
    parser.add_argument('-i', '--input', metavar='FILE', nargs='*',
        help='Text file(s) containing input data (defaults to stdin)')
    parser.add_argument('-d', '--dict', metavar='FILE',
        help='Restore and extend dictionary in file (json)')
    parser.add_argument('-o', '--output', metavar='FILE',
        help='Output of the babbelbot (defaults to stdout)')
    parser.add_argument('-a', '--about', metavar='STRING',
        help='Give a word that should be included in the generated text')
    parser.add_argument('-l', '--length', metavar='INT', type=int,
        help='Number of sentences to generate (length may vary) default: 1',
        default=1)
    parser.add_argument('-g', '--gibber', action='store_true',
        help='Create gibberish, make up the words')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='No output - just consume input')
    args = parser.parse_args()

    c = Chatter()

    # restore memory
    if args.dict and os.path.exists(args.dict):
        with open(args.dict, encoding='utf-8') as f:
            s = f.read()
        if s.strip():
            try:
                c.read_dict(json.loads(s))
            except (ValueError, KeyError):
                sys.stderr.write('Cannot read dict file. Exiting.\n')
                exit(1)

    # consume input - stdin only if something is piped in
    if args.input:
        for name in args.input:
            with open(name, 'rb') as f:
                c.learn(decode(f.read()))
    elif not sys.stdin.isatty():
        c.learn(decode(sys.stdin.buffer.read()))

    if EDGE not in c.words:
        sys.stderr.write('Nothing learned yet - feed me some text.\n')
        exit(1)

    # now lets babbel a bit
    if not args.quiet:
        if args.output:
            out_file = open(args.output, 'w', encoding='utf-8')
        else:
            out_file = sys.stdout
            out_file.reconfigure(encoding='utf-8')
        for _ in range(0, args.length):
            if args.gibber:
                out_file.write(c.gibber())
            else:
                out_file.write(c.babbel(args.about))
            out_file.write('\n')
        out_file.flush()

    # spit out what has been learned
    if args.dict:
        with open(args.dict, 'w', encoding='utf-8') as f:
            json.dump(c.dump_memory(), f, ensure_ascii=False)

    exit(0)
