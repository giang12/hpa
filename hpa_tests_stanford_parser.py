#!/usr/bin/python

import os
import nltk
import shlex

import atexit
from subprocess import Popen, PIPE
from os.path import join
import logging
import re

from nltk import ParentedTree



STANFORD_DIR = "/home/carneyadmin/Desktop/stanford-parser-2012-07-09"
STANFORD_JAR_FILE = "stanford-parser.jar"
STANFORD_GRAMMAR_PATH = "/".join([STANFORD_DIR, "grammar"])
STANFORD_GRAMMAR_FILE = "englishPCFG.ser.gz"


stanford_parser = None

def ensure_stanford_parser_running():
    """
    java -mx1024m -cp "$scriptdir/stanford-parser.jar:" edu.stanford.nlp.parser.lexparser.LexicalizedParser \
     -outputFormat "penn,typedDependencies" $scriptdir/grammar/englishPCFG.ser.gz $*
    """
    global stanford_parser
    if stanford_parser is None:
        cmd = 'java -Xmx1024m -cp "%(DIR)s/%(JAR_FILE)s:" edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat "penn,typedDependencies" %(GRAMMAR_PATH)s/%(GRAMMAR_FILE)s -' % dict(
            DIR=STANFORD_DIR,
            JAR_FILE=STANFORD_JAR_FILE, GRAMMAR_PATH=STANFORD_GRAMMAR_PATH,
            GRAMMAR_FILE=STANFORD_GRAMMAR_FILE)
#        print "cmd is %s" % cmd
        args = shlex.split(cmd)
#	print args
        stanford_parser = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)


def stop_stanford_parser_process():
    global stanford_parser
    if stanford_parser is not None:
        stanford_parser.terminate()
        stanford_parser = None


def stanford_tree(sentence):
    ensure_stanford_parser_running()
    # Sanitize the input a little bit
    if not sentence.endswith(tuple(".!?")):
        sentence += "."
    stanford_parser.stdin.write('%s\n-\n' % sentence)
    #    stanford_parser.stdin.write('%s\n\n%s' % (sentence, ascii.ctrl('d')))  # ctrl-d doesn't work :(
    # prepare to read the output from the parser
    trees = []
    dependencies = []
    num_sentences = len(nltk.sent_tokenize(sentence))
    for i in range(0, num_sentences):
        blanks_seen = 0  # flag to count the number of \n lines seen; stop reading after seeing the 2nd one
        tree_string, dependencies_string = "", ""  # output holders
        while True:
            # the java parser prints its output for a sentence in two chunks, separated by a blank line.
            # the first chunk is the parse tree,
            # the second is a list of dependencies.
            # so what we're seeing when we readline can be determined by the number of blank lines we have seen
            # to this point.
            line = stanford_parser.stdout.readline()
            if line == '\n':
                blanks_seen += 1  # this means we're done with the Tree, now we are going to see the dependencies
            if blanks_seen == 2:  # this means we're done with this sentence, so break out of the while
                break
            if blanks_seen == 0:  # add this line to the tree
                tree_string += line
            elif blanks_seen == 1:  # add this line to the dependencies
                dependencies_string += line
            else:
                assert False, "blanks_seen can only be 0 or 1 but it is %d." % blanks_seen
        # we're done with a sentence, so parse the tree and extract the dependencies and add them to the lists
        trees.append(ParentedTree.parse(tree_string))
        dependencies.append(tuple([d for d in dependencies_string.split("\n") if d]))
    sentence_parses_and_dependencies = zip(trees, dependencies)
    #for i, (tree, dependencies) in enumerate(sentence_parses_and_dependencies):
    #    print "Parser tree for sentence %d: %s  Parser dependencies for sentence %d: %s" % (i, tree, i, dependencies)
    return sentence_parses_and_dependencies



def sentence2tree(sentence = ""):
    tree1 = stanford_tree(sentence)[0][0]
    return tree1

if __name__ == "__main__":
    sentence1 = "Would you get me a taxi at 10 in the morning?"
    tree = sentence2tree(sentence1)
    print tree
