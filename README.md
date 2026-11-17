Chatter
=======

Babbel Bot - builds Markov-Chains by given text and uses them to generate text.

Requires Python 3. Input may be plain text (UTF-8 or Latin-1 encoded) or
epub files, e.g. from https://projekt-gutenberg.org/.

Run the tests with `python -m unittest test_chatter`.

Usage as python module
----------------------

Let's teach the bot a passage from "The Zen of Python", by Tim Peters. The
passage is tiny, so we let the bot look back only one word (`order=1`):

```python
>>> import chatter as c
>>> bot = c.Chatter(order=1)
>>> bot.learn("Beautiful is better than ugly.")
>>> bot.learn("Explicit is better than implicit.")
>>> bot.learn("Simple is better than complex.")
>>> bot.learn("Complex is better than complicated.")
>>> bot.learn("Flat is better than nested.")
>>> bot.learn("Sparse is better than dense.")
>>> bot.babbel()
'explicit is better than complicated!'
>>> bot.babbel('better')
'simple is better than complex is better than complicated.'
>>> bot.babbel('love')
'simple is better than implicit?'
>>> bot.gibber()
'cicompl ber tethan t et?'
>>> bot.create_word()
'itteanex'
>>>
>>> knowledge = bot.dump_memory()
>>> knowledge['words']['dsc']['than']
{'ugly': 1, 'implicit': 1, 'complex': 1, 'complicated': 1, 'nested': 1, 'dense': 1}
>>> knowledge['words']['asc']['than']
{'better': 6}
>>> knowledge['stats']
{'words': {'count': 6.0, 'avg': 5.0}, 'chars': {'count': 30.0, 'avg': 5.1000000000000005}}
```

The 'dsc' chain maps the last `order` words (joined by spaces) to the words
that followed them, the 'asc' chain maps the next `order` words to the words
that preceded them. The empty string marks the start and end of a sentence.
The same is done for the characters of words in `knowledge['chars']`.

In the 'stats' dict we have 'chars' which holds the statistics of characters per word, the 'words' hold the statistics for words per sentence.

How much the bot looks back
---------------------------

`order` (default 2) is the number of preceding words that pick the next one.
With Goethe's Werther from `sample_data`:

| order | sample |
|-------|--------|
| 1 | sagte sie grüßte mich frühlingsluft. |
| 2 | ich war ausgestiegen und eine trübe wolke lag über ihrem auge. |
| 3 | so reizend als es mir war so einförmig würde es in der erzählung werden! (that's Goethe verbatim) |

Low orders are word salad, high orders mostly quote the input. The bigger the
input, the higher the order can go before it starts quoting.

Usage from the command line
---------------------------

Let's assume we have the zen of python in a file called zen.txt. 

```sh
$ ./chatter.py --help
usage: chatter.py [-h] [-i [FILE ...]] [-d FILE] [-o FILE] [-a STRING]
                  [-l INT] [-g] [-q] [-n INT] [-c]

Generate random sentences and words from specified input files.

options:
  -h, --help            show this help message and exit
  -i [FILE ...], --input [FILE ...]
                        Text or epub file(s) containing input data (defaults
                        to stdin)
  -d FILE, --dict FILE  Restore and extend dictionary in file (json)
  -o FILE, --output FILE
                        Output of the babbelbot (defaults to stdout)
  -a STRING, --about STRING
                        Give a word that should be included in the generated
                        text
  -l INT, --length INT  Number of sentences to generate (length may vary)
                        default: 1
  -g, --gibber          Create gibberish, make up the words
  -q, --quiet           No output - just consume input
  -n INT, --order INT   Number of preceding words (or chars) that determine
                        the next one - higher is more coherent, but closer to
                        the input. default: 2, or what the dictionary was
                        built with
  -c, --chat            Chat with the bot - it replies about the words you
                        use and learns from them

$ cat zen.txt | ./chatter.py -d knowledge.json -n 1
the temptation to guess?

$ ./chatter.py -d knowledge.json
the implementation is better than complicated?

$ ./chatter.py -d knowledge.json --about special
special cases aren't special enough to guess?

$ ./chatter.py -d knowledge.json --gibber
bl heris imes as nkish n plis iabeali.
```
Chatting
--------

With `--chat` the bot answers what you type. It picks a word of your message
it knows - preferably a rare one, since those carry the topic - and babbels
about it. Afterwards it learns your message, so with `-d` the conversation
ends up in its dictionary. An empty line ends the chat.

```sh
$ ./chatter.py -i sample_data/Goethe_Werther.txt --chat
Talk to me - an empty line ends the chat.
> Was macht dein Herz?
mit drei schritten mess ich dein grab o du warst schön schön wie reizend sie für eindrücke macht.
> Ich liebe dich, Lotte
doch süßer die stimme nie erwacht er auf dich hat auf dich du allliebender?
>
```

In Python: `bot.reply("Was macht dein Herz?")`.

BTW meta-fun: teach the bot some python code and see if it runs ;)
