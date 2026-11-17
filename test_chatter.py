import json, os, random, subprocess, sys, tempfile, unittest

import chatter as c

HERE = os.path.dirname(os.path.abspath(__file__))
ZEN = [
    "Beautiful is better than ugly.",
    "Explicit is better than implicit.",
    "Simple is better than complex.",
    "Complex is better than complicated.",
    "Flat is better than nested.",
    "Sparse is better than dense.",
]


class ChatterTest(unittest.TestCase):
    def setUp(self):
        random.seed(42)

    def test_single_sentence_is_reproduced_including_first_word(self):
        bot = c.Chatter()
        bot.learn("Hello wonderful world.")
        for _ in range(20):
            self.assertEqual(bot.babbel()[:-1], "hello wonderful world")

    def test_babbel_about_contains_word(self):
        bot = c.Chatter()
        for line in ZEN:
            bot.learn(line)
        for _ in range(20):
            self.assertIn("nested", bot.babbel("nested")[:-1].split())

    def test_babbel_about_unknown_word_falls_back(self):
        bot = c.Chatter()
        bot.learn("Hello world.")
        self.assertEqual(bot.babbel("love")[:-1], "hello world")

    def test_commas_do_not_end_sentences(self):
        bot = c.Chatter()
        bot.learn("One, two, three.")
        self.assertEqual(bot.stats['words']['avg'], 3)

    def test_gibber_and_create_word(self):
        bot = c.Chatter()
        for line in ZEN:
            bot.learn(line)
        self.assertTrue(bot.create_word())
        self.assertIn(bot.gibber()[-1], '.!?')

    def test_umlauts_survive(self):
        bot = c.Chatter()
        bot.learn("Daß ist schön!")
        self.assertEqual(bot.babbel()[:-1], "daß ist schön")

    def test_memory_round_trips_through_json(self):
        bot = c.Chatter(order=2)
        for line in ZEN:
            bot.learn(line)
        memory = json.loads(json.dumps(bot.dump_memory()))
        other = c.Chatter()
        other.read_dict(memory)
        self.assertEqual(other.order, 2)
        self.assertEqual(other.dump_memory(), bot.dump_memory())

    def test_higher_order_reproduces_unambiguous_text(self):
        # with one word of lookback "is" is ambiguous, with two it is not
        text = "the cat is here. the dog is there."
        bot = c.Chatter(order=2)
        bot.learn(text)
        for _ in range(20):
            self.assertIn(bot.babbel()[:-1],
                          ["the cat is here", "the dog is there"])
            self.assertEqual(bot.babbel("here")[:-1], "the cat is here")

    def test_about_works_with_higher_order(self):
        bot = c.Chatter(order=4)
        for line in ZEN:
            bot.learn(line)
        for _ in range(20):
            self.assertEqual(bot.babbel("nested")[:-1],
                             "flat is better than nested")

    def test_reply_is_about_the_rare_word(self):
        bot = c.Chatter(order=1)
        for line in ZEN:
            bot.learn(line)
        # 'is' is known six times, 'nested' once
        replies = [bot.reply("Is it nested?") for _ in range(50)]
        about_nested = [r for r in replies if 'nested' in r[:-1].split()]
        self.assertGreater(len(about_nested), 35)

    def test_reply_to_unknown_words_babbels(self):
        bot = c.Chatter()
        bot.learn("Hello world.")
        self.assertEqual(bot.reply("Wie geht's?")[:-1], "hello world")

    def test_decode_falls_back_to_latin1(self):
        self.assertEqual(c.decode("daß".encode('latin-1')), "daß")
        self.assertEqual(c.decode("daß".encode('utf-8')), "daß")


class CommandLineTest(unittest.TestCase):
    def run_cli(self, *args, stdin=b''):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, 'chatter.py')] + list(args),
            input=stdin, capture_output=True, check=True).stdout.decode('utf-8')

    def test_learn_save_and_restore_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            dict_file = os.path.join(tmp, 'knowledge.json')
            self.run_cli('-d', dict_file, '-q', '-o', os.devnull,
                         stdin="Wie froh bin ich.".encode('utf-8'))
            out = self.run_cli('-d', dict_file, '-l', '3')
            self.assertEqual(out.split('\n')[0].strip()[:-1],
                             "wie froh bin ich")

    def test_chat_replies_and_learns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'in.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write("Hello wonderful world.")
            dict_file = os.path.join(tmp, 'knowledge.json')
            out = self.run_cli('-i', path, '-d', dict_file, '-c',
                               stdin="Tell me about the world\n"
                                     "Grüße aus Köln\n".encode('utf-8'))
            self.assertIn("hello wonderful world", out)
            with open(dict_file, encoding='utf-8') as f:
                self.assertIn("aus köln", json.load(f)['words']['dsc'])

    def test_reads_latin1_input_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'in.txt')
            with open(path, 'wb') as f:
                f.write("Daß ist schön.".encode('latin-1'))
            out = self.run_cli('-i', path)
            self.assertEqual(out.strip()[:-1], "daß ist schön")


if __name__ == '__main__':
    unittest.main()
