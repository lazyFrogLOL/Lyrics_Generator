# -*- coding: utf-8 -*-
import os
import codecs
import collections
from six.moves import cPickle
import numpy as np
import re
import itertools
import poetrytools as pt
import itertools
class TextLoader():
    def __init__(self, data_dir, batch_size, seq_length, encoding=None):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.seq_length = seq_length

        input_file = os.path.join(data_dir, "input.txt")
        vocab_file = os.path.join(data_dir, "vocab.pkl")
        tensor_file = os.path.join(data_dir, "data.npy")

        # Let's not read voca and data from file. We many change them.
        if True or not (os.path.exists(vocab_file) and os.path.exists(tensor_file)):
            print("reading text file")
            self.preprocess(input_file, vocab_file, tensor_file, encoding)
        else:
            print("loading preprocessed files")
            self.load_preprocessed(vocab_file, tensor_file)
        self.create_batches()
        self.reset_batch_pointer()

    def clean_str(self, string):
        """
        Tokenization/string cleaning for all datasets except for SST.
        Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data
        """
        # string = re.sub(r"[^가-힣A-Za-z0-9(),!?\'\`]", " ", string)
        # string = re.sub(r"\'s", " \'s", string)
        # string = re.sub(r"\'ve", " \'ve", string)
        # string = re.sub(r"n\'t", " n\'t", string)
        # string = re.sub(r"\'re", " \'re", string)
        # string = re.sub(r"\'d", " \'d", string)
        # string = re.sub(r"\'ll", " \'ll", string)
        # string = re.sub(r",", " , ", string)
        # string = re.sub(r"!", " ! ", string)
        # string = re.sub(r"\(", " \( ", string)
        # string = re.sub(r"\)", " \) ", string)
        # string = re.sub(r"\?", " \? ", string)
        # string = re.sub(r"\s{2,}", " ", string)
        string = string.replace('\r\n', ' *BREAK* ').replace('\n', ' *BREAK* ').replace('  ', ' ')
        return string.strip().lower()

    def build_vocab(self, sentences):
        """
        Builds a vocabulary mapping from word to index based on the sentences.
        Returns vocabulary mapping and inverse vocabulary mapping.
        """
        # Build vocabulary
        word_counts = collections.Counter(sentences)
        # Mapping from index to word
        vocabulary_inv = [x[0] for x in word_counts.most_common()]
        vocabulary_inv = list(sorted(vocabulary_inv))
        # Mapping from word to index
        vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
        return [vocabulary, vocabulary_inv]

    def preprocess(self, input_file, vocab_file, tensor_file, encoding):
        with codecs.open(input_file, "r", encoding=encoding) as f:
            data = f.read()

        lyrics = pt.tokenize(data)
        for i in range(0,len(lyrics)):
<<<<<<< HEAD
            lyrics[i].insert(0,'<go>')
        for i in range(0,len(lyrics)-1):
            if(len(lyrics[i]) > 1 and len(lyrics[i + 1]) > 1):
                if(pt.rhymes(lyrics[i][-2],lyrics[i+1][-2],1)):
                    lyrics[i].append('<endLine>')
                    lyrics[i+1].append('<endLine>')
        for i in range(0, len(lyrics)):
            lyrics[i].append('<eos>')  
        complete_lyrics_list = [x for x in lyrics if not len(x) == 3 and not x[1] == ""]
        for i in range(0,len(complete_lyrics_list)):
            print(complete_lyrics_list[i])
        
        lyrics_list = list(itertools.chain.from_iterable(complete_lyrics_list))
=======
            lyrics[i].append('*breakLine*')
            lyrics[i].insert(0,'*headLine*')
        for i in range(0,len(lyrics)-1):
            if(len(lyrics[i]) > 1 and len(lyrics[i + 1]) > 1):
                if(pt.rhymes(lyrics[i][-2],lyrics[i+1][-2],1)):
                    lyrics[i].append('*endLine*')
                    lyrics[i+1].append('*endLine*')
        lyrics_list = list(itertools.chain.from_iterable(lyrics))
        # Optional text cleaning or make them lower case, etc.
        # data = self.clean_str(data)
        # x_text = data.split()

>>>>>>> d369378359131c5f405b4f241b995c81f068086a

        self.vocab, self.words = self.build_vocab(lyrics_list)
        self.vocab_size = len(self.words)

        with open(vocab_file, 'wb') as f:
            cPickle.dump(self.words, f)

        #The same operation like this [self.vocab[word] for word in x_text]
        # index of words as our basic data
        self.tensor = np.array(list(map(self.vocab.get, lyrics_list)))
        # Save the data to data.npy
        np.save(tensor_file, self.tensor)

    def load_preprocessed(self, vocab_file, tensor_file):
        with open(vocab_file, 'rb') as f:
            self.words = cPickle.load(f)
        self.vocab_size = len(self.words)
        self.vocab = dict(zip(self.words, range(len(self.words))))
        self.tensor = np.load(tensor_file)
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))

    def create_batches(self):
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))
        if self.num_batches==0:
            assert False, "Not enough data. Make seq_length and batch_size small."

        self.tensor = self.tensor[:self.num_batches * self.batch_size * self.seq_length]
        xdata = self.tensor
        ydata = np.copy(self.tensor)

        ydata[:-1] = xdata[1:]
        ydata[-1] = xdata[0]
        self.x_batches = np.split(xdata.reshape(self.batch_size, -1), self.num_batches, 1)
        self.y_batches = np.split(ydata.reshape(self.batch_size, -1), self.num_batches, 1)

    def next_batch(self):
        x, y = self.x_batches[self.pointer], self.y_batches[self.pointer]
        self.pointer += 1
        return x, y

    def reset_batch_pointer(self):
        self.pointer = 0