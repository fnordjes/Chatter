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
        bot = c.Chatter()
        for line in ZEN:
            bot.learn(line)
        memory = json.loads(json.dumps(bot.dump_memory()))
        other = c.Chatter()
        other.read_dict(memory)
        self.assertEqual(other.dump_memory(), bot.dump_memory())

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

    def test_reads_latin1_input_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'in.txt')
            with open(path, 'wb') as f:
                f.write("Daß ist schön.".encode('latin-1'))
            out = self.run_cli('-i', path)
            self.assertEqual(out.strip()[:-1], "daß ist schön")


if __name__ == '__main__':
    unittest.main()
