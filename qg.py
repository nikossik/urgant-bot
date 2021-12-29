from tqdm import tqdm
from parse import Parser

from question_generation.pipelines import pipeline

import transformers
from deep_translator import GoogleTranslator

class QgTrans:
    def __init__(self, translator_ru_to_en, translator_en_to_ru, nlp):
        self.translator_ru_to_en = translator_ru_to_en
        self.translator_en_to_ru = translator_en_to_ru
        self.nlp = nlp


    def preprocessing(self, corpus, lim=4999):
        n = 0
        for i in range(len(corpus)):
            if len(corpus[i-n]) == 0:
                corpus.pop(i-n)
                n+=1
                continue
            corpus[i-n] = corpus[i-n].replace('\xa0', ' ')[:lim]

        return corpus

    def parse(self, name,):
        parser = Parser()
        return parser.parse(name)        


    def translate_ru_to_en(self, sentence):
        translated = []
        
        for text in sentence.split('.'):
            translated.append(self.translator_ru_to_en.translate(text=sentence))

        return translated


    def qg_en_to_en(self, corpus):
        qg = []
        for i in corpus:
            qg.append(self.nlp(i))
        return qg


    def translate_en_to_ru(self, sentence):
        return self.translator_en_to_ru.translate(text=sentence)


    def predict(self, name):
        ru_to_en = []
        en_to_ru = []
        corpus = self.parse(name,)
        print(corpus)
        corpus = self.preprocessing(corpus)[:9]
        for text in tqdm(corpus):
            ru_to_en.append(self.translate_ru_to_en(text))
        qg = self.qg_en_to_en(ru_to_en)
        return qg















