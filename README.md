Chatter
=======

Babbel Bot - builds Markov-Chains by given text and uses them to generate text.

Usage as python module
----------------------

Let' teach the bot a passage from "The Zen of Python", by Tim Peters:

```python
>>> import chatter as c
>>> bot = c.Chatter()
>>> bot.learn("Beautiful is better than ugly.")
>>> bot.learn("Explicit is better than implicit.")
>>> bot.learn("Simple is better than complex.")
>>> bot.learn("Complex is better than complicated.")
>>> bot.learn("Flat is better than nested.")
>>> bot.learn("Sparse is better than dense.")
>>> bot.babbel()
'flat is better than complex is better?'
>>> bot.babbel('better')
'simple is better better than ugly.'
>>> bot.babbel('love')
'flat is better than implicit.'
>>> bot.gibber()
'ben isicompl comply t tetter?'
>>> bot.create_word()
'compan'
>>>
>>> knowledge = bot.dump_memory()
>>> knowledge['words']['than']
# output is formatted, just for you
{
    'asc': {
      'better': 6
    },
    'dsc': {
        'dense': 1,
        'nested': 1,
        'ugly': 1,
        'complex': 1,
        'complicated': 1,
        'implicit': 1
    }
}
>>> knowledge['stats']
{'chars': {'count': 30.0, 'avg': 5.1000000000000005}, 'words': {'count': 6.0, 'avg': 5.0}}
```

In the 'stats' dict we have 'chars' which holds the statistics of characters per word, the 'words' hold the statistics for words per sentence.

Usage from the command line
---------------------------

Let's assume we have the zen of python in a file called zen.txt. 

```sh
$ ./chatter.py --help
usage: chatter.py [-h] [-i [FILE [FILE ...]]] [-d FILE] [-o FILE] [-l INT]
                  [-g]

Generate random sentences and words from specified input files.

optional arguments:
  -h, --help            show this help message and exit
  -i [FILE [FILE ...]], --input [FILE [FILE ...]]
                        Text file(s) containing input data (defaults to stdin)
  -d FILE, --dict FILE  Restore and extend dictionary in file
  -o FILE, --output FILE
                        Output of the babbelbot (defaults to stdout)
  -a STRING, --about STRING
                        Give a word that should be included in the generated
                        text
  -l INT, --length INT  Number of sentences to generate (length may vary)
                        default: 1
  -g, --gibber          Create gibberish, make up the words

$ cat zen.txt | ./chatter.py -d knowledge.dict 
the temptation to guess?

$ echo "" | ./chatter.py -d knowledge.dict 
the implementation is better than complicated?

$ echo "" | ./chatter.py -d knowledge.dict --about special
special cases aren't special enough to guess?

$ ./chatter.py -d knowledge.dict -gibber
bl heris imes as nkish n plis iabeali.
```
BTW meta-fun: teach the bot some python code and see if it runs ;)
