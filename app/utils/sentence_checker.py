import nltk.corpus
from nltk import download

class SentenceChecker:
    def __init__(self):
        try:
            self.words = set(nltk.corpus.words.words())
        except LookupError:
            download('words')
            self.words = set(nltk.corpus.words.words())
            
    def is_sentence_meaningless(self, sentence):
        """
        Check if all words in the input sentence do not contain in the set of English word (retrieved from nltk's corpus words data)
        """
        return all([word not in self.words for word in sentence.lower().split()])