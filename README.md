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
>>> bot.gibber()
'ben isicompl comply t tetter?'
>>> 
```

Usage from the command line
---------------------------

```sh
$ ./chatter.py -h
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
  -l INT, --length INT  Number of sentences to generate (length may vary)
                        default: 1
  -g, --gibber          Create gibberish, make up the words

```
