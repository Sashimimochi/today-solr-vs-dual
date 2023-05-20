from gensim.models import word2vec, KeyedVectors
import MeCab
import numpy as np
from config import MODEL

class Vectorizer:
    def __init__(self) -> None:
        model_path = MODEL.get('model_path')
        binary = MODEL.get('binary')
        model_format = MODEL.get('model_format')
        if model_format == 'vector_only':
            self.model = KeyedVectors.load_word2vec_format(model_path, binary=binary)
        else:
            self.model = word2vec.Word2Vec.load(model_path)
        path = "/usr/lib/x86_64-linuxgnu/mecab/dic/mecab-ipadic-neologd"
        self.mt = MeCab.Tagger(path) # 形態素解析器

    def _vectorize(self, word) -> None:
        return self.model.wv.get_vector(word)

    def text_vectorize(self, text):
        sum_vec = np.zeros(self.model.vector_size)
        word_count = 0
        node = self.mt.parseToNode(text)
        while node:
            fields = node.feature.split(',')
            word = node.surface
            if fields[0] in ['名詞', '動詞', '形容詞'] and word in self.model.wv.vocab.keys():
                sum_vec += self._vectorize(word)
                word_count += 1
            node = node.next
        return sum_vec / word_count
