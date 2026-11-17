#!/usr/bin/env python3

import re, random, argparse, json, sys, os.path, io, zipfile, posixpath
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote

# marks the start and the end of sentences and words (json has no None keys)
EDGE = ''

def decode(data):
    # most texts are utf-8 nowadays, old ones often latin-1
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')

def read_text(data):
    # epubs are zip files, everything else is taken as plain text
    if data.startswith(b'PK'):
        return read_epub(data)
    return decode(data)

def read_epub(data):
    book = zipfile.ZipFile(io.BytesIO(data))
    # the container points to the package file, which lists the chapters
    # (manifest) and their reading order (spine)
    container = ET.fromstring(book.read('META-INF/container.xml'))
    opf_path = container.find('.//{*}rootfile').get('full-path')
    package = ET.fromstring(book.read(opf_path))
    hrefs = {item.get('id'): item.get('href')
             for item in package.iterfind('.//{*}manifest/{*}item')}
    text = []
    for itemref in package.iterfind('.//{*}spine/{*}itemref'):
        path = posixpath.join(posixpath.dirname(opf_path),
                              unquote(hrefs[itemref.get('idref')]))
        extractor = TextExtractor()
        extractor.feed(decode(book.read(path)))
        text.append(''.join(extractor.text))
    return '\n'.join(text)

class TextExtractor(HTMLParser):
    # end a sentence after blocks, so headings don't run into the text
    BLOCKS = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'}
    SKIP = {'head', 'script', 'style'}

    def __init__(self):
        super().__init__()
        self.text = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skipping += 1
        elif tag == 'br':
            self.text.append(' ')

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skipping -= 1
        elif tag in self.BLOCKS:
            self.text.append('.\n')

    def handle_data(self, data):
        if not self.skipping:
            self.text.append(data)

class Chatter(object):
    def __init__(self, order=2):
        # how many preceding words (or chars) determine the next one
        self.order = order
        self.chars = self.new_chain()
        self.words = self.new_chain()
        self.counts = None

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
        self.counts = None
        text = text.lower()
        # commas don't end a sentence, so they're not split on
        sentences = re.split(r'\s*[()"!?.;:]+\s*', text)
        for sentence in sentences:
            word_list = self.split_words(sentence)

            # skip if there's nothing to do
            if not word_list:
                continue

            self.learn_sequence(word_list, self.words)
            for word in word_list:
                self.learn_sequence(list(word), self.chars)
                self.__update_average(len(word), self.stats['chars'])

            self.__update_average(len(word_list), self.stats['words'])

    def learn_sequence(self, items, chain):
        n = self.order
        # 'dsc': which item follows the n items before it, padded with EDGE
        # so the start is known and EDGE follows the last item
        padded = [EDGE] * n + items + [EDGE]
        for i in range(n, len(padded)):
            self.increment_key(padded[i - n:i], padded[i], chain['dsc'])
        # 'asc': which item precedes the n items after it, to be able to
        # create sentences from back to start
        padded = [EDGE] + items + [EDGE] * n
        for i in range(0, len(items) + 1):
            self.increment_key(padded[i + 1:i + 1 + n], padded[i], chain['asc'])

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
        about = about.lower() if about else None
        sentence = self.generate(self.words, self.stats['words'], about)
        return ' '.join(sentence) + self.select_weighted(self.delims)

    def reply(self, text):
        # talk about a word of the message - preferably a rare one, since
        # those carry the topic while frequent ones are 'the', 'and', ...
        counts = self.word_counts()
        rarity = {}
        for word in self.split_words(text.lower()):
            if word in counts:
                rarity[word] = 1.0 / counts[word]
        if not rarity:
            return self.babbel()
        return self.babbel(self.select_weighted(rarity))

    def word_counts(self):
        # counting is slow for big books, so remember it until learning more
        if self.counts is None:
            self.counts = self.count_words()
        return self.counts

    def count_words(self):
        counts = {}
        for followers in self.words['dsc'].values():
            for word, count in followers.items():
                if word != EDGE:
                    counts[word] = counts.get(word, 0) + count
        return counts

    def create_word(self):
        return ''.join(self.generate(self.chars, self.stats['chars']))

    def generate(self, chain, stats, about=None):
        # safety net only - sequences usually end by reaching EDGE
        limit = int(stats['avg'] * 3) + 1

        # start from a window of n items ending in 'about' if possible,
        # otherwise from the start of a sequence
        windows = {}
        if about:
            for key, followers in chain['dsc'].items():
                if key.split(' ')[-1] == about:
                    windows[key] = sum(followers.values())
        if windows:
            window = self.select_weighted(windows).split(' ')
        else:
            window = [EDGE] * self.order
        sequence = [item for item in window if item != EDGE]

        # climb up the chain until a starter is found
        state = window
        while state[0] != EDGE and len(sequence) < limit:
            item = self.select_weighted(chain['asc'][self.key(state)])
            if item == EDGE:
                break
            sequence.insert(0, item)
            state = [item] + state[:-1]

        # build the rest of the sequence climbing the chain down
        state = window
        while len(sequence) < limit:
            item = self.select_weighted(chain['dsc'][self.key(state)])
            if item == EDGE:
                break
            sequence.append(item)
            state = state[1:] + [item]
        return sequence

    def dump_memory(self):
        return {
            'order': self.order,
            'chars': self.chars,
            'words': self.words,
            'stats': self.stats
        }

    def read_dict(self, dictionary):
        self.order = dictionary['order']
        self.chars = dictionary['chars']
        self.words = dictionary['words']
        self.stats = dictionary['stats']
        self.counts = None

    def __update_average(self, count, stats):
        stats['count'] += 1
        stats['avg'] += (float(count) - stats['avg']) / float(stats['count'])

    @staticmethod
    def split_words(sentence):
        words = re.findall(r'[\w\d]+[\-\']{0,1}[\w\d]+|[\w\d]+', sentence)
        # plain numbers are mostly chapter or verse numbers, not words
        return [word for word in words if not word.isdigit()]

    @staticmethod
    def new_chain():
        return {'asc': {}, 'dsc': {}}

    @staticmethod
    def key(items):
        # words and chars never contain spaces, so this is unambiguous and
        # keeps the keys json-friendly
        return ' '.join(items)

    @staticmethod
    def increment_key(items, follower, dictionary):
        followers = dictionary.setdefault(Chatter.key(items), {})
        followers[follower] = followers.get(follower, 0) + 1

    @staticmethod
    def select_weighted(dictionary):
        random_pick = random.uniform(0, sum(dictionary.values()))
        total = 0.0
        for key, value in dictionary.items():
            total += value
            if random_pick < total: return key
        return key

def chat(bot):
    print('Talk to me - an empty line ends the chat.')
    while True:
        try:
            line = input('> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            break
        print(bot.reply(line))
        # learn after replying, otherwise the bot just parrots the line
        bot.learn(line)

def talk(bots, turns, about=None):
    # one bot opens, then each turn another one replies to the last line
    speaker = random.choice(list(bots))
    line = bots[speaker].babbel(about)
    print('%s: %s' % (speaker, line))
    for _ in range(1, turns):
        speaker = random.choice([name for name in bots if name != speaker])
        line = bots[speaker].reply(line)
        print('%s: %s' % (speaker, line))

def load(bot, file_name):
    with open(file_name, encoding='utf-8') as f:
        s = f.read()
    if s.strip():
        try:
            bot.read_dict(json.loads(s))
        except (ValueError, KeyError):
            sys.stderr.write('Cannot read dict file %s. Exiting.\n' % file_name)
            exit(1)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=
        'Generate random sentences and words from specified input files.')
    parser.add_argument('-i', '--input', metavar='FILE', nargs='*',
        help='Text or epub file(s) containing input data (defaults to stdin)')
    parser.add_argument('-d', '--dict', metavar='FILE',
        help='Restore and extend dictionary in file (json)')
    parser.add_argument('-o', '--output', metavar='FILE',
        help='Output of the babbelbot (defaults to stdout)')
    parser.add_argument('-a', '--about', metavar='STRING',
        help='Give a word that should be included in the generated text')
    parser.add_argument('-l', '--length', metavar='INT', type=int,
        help='Number of sentences to generate (length may vary) default: 1, '
             'or 10 with --talk')
    parser.add_argument('-g', '--gibber', action='store_true',
        help='Create gibberish, make up the words')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='No output - just consume input')
    parser.add_argument('-n', '--order', metavar='INT', type=int,
        help='Number of preceding words (or chars) that determine the next '
             'one - higher is more coherent, but closer to the input. '
             'default: 2, or what the dictionary was built with')
    parser.add_argument('-c', '--chat', action='store_true',
        help='Chat with the bot - it replies about the words you use and '
             'learns from them')
    parser.add_argument('-t', '--talk', metavar='FILE', nargs='+',
        help='Let the bots of these dictionaries (json) talk to each other, '
             'they are named after the files and do not learn')
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding='utf-8')
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding='utf-8')

    if args.talk:
        bots = {}
        for file_name in args.talk:
            name = os.path.splitext(os.path.basename(file_name))[0]
            bots[name] = Chatter()
            load(bots[name], file_name)
        if len(bots) < 2:
            sys.stderr.write('It takes two to talk. Exiting.\n')
            exit(1)
        talk(bots, args.length or 10, args.about)
        exit(0)

    c = Chatter(args.order or 2)

    # restore memory
    if args.dict and os.path.exists(args.dict):
        load(c, args.dict)
        if args.order and args.order != c.order:
            sys.stderr.write('Dict file was built with order %d. '
                             'Exiting.\n' % c.order)
            exit(1)

    # consume input - stdin only if something is piped in and isn't the chat
    if args.input:
        for name in args.input:
            with open(name, 'rb') as f:
                c.learn(read_text(f.read()))
    elif not args.chat and not sys.stdin.isatty():
        c.learn(decode(sys.stdin.buffer.read()))

    if not c.words['dsc']:
        sys.stderr.write('Nothing learned yet - feed me some text.\n')
        exit(1)

    # now lets babbel a bit
    if args.chat:
        chat(c)
    elif not args.quiet:
        if args.output:
            out_file = open(args.output, 'w', encoding='utf-8')
        else:
            out_file = sys.stdout
        for _ in range(0, args.length or 1):
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
