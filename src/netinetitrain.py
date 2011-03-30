import nltk
import random

from utilities import build_table, get_basic_features, split_get

def get_algorithm(algorithm):
    """A factory function to get the proper algorithm"""
    algorithms = {
        'NB': nltk.NaiveBayesClassifier,
        # This MaxentClassifier doesn't exist
#        'ME': nltk.MaxentClassifier,
        'DT': nltk.DecisionTreeClassifier,
    }
    return algorithms[algorithm].train

class NetiNetiTrain:
    """A class that defines the training algorithm and the training files and 
    actually trains a natrual language toolkit object (nltk)

    """
    def __init__(self, species_train="data/New_sp_contexts.txt",
                 irrelevant_text="data/pictorialgeo.txt",
                 all_names="data/millionnames.txt", learning_algo="NB",
                 num_tok_train=10000, num_neg_tg=5000, context_span=1):
        # TODO Too many arguments, perhaps create a TrainingFiles Class?
        """Builds and trains the NetiNeti model

        Keyword arguments:
        species_train -- describe arg (default "data/New_sp_contexts.txt")
        irrelevant_text -- a lot of words without any species whatsoever (default "data/pictorialgeo.txt")
        all_names -- list of a lot of actual species data (default "data/millionnames.txt")
        learning_algo -- the algorithm to train with (default "NB")
        num_tok_train -- number of positive training tokens (default 10000)
        num_neg_tg -- number of negative trigram features(default 5000)
        context_span -- describe arg (default 1)

        """
        self.contexts = split_get(species_train)
        self.irrelevant_text = open(irrelevant_text).read()
        self._num_tok = num_tok_train
        self._num_neg_tg = num_neg_tg
        self._context_span = context_span
        self._all_names = split_get(all_names)
        self.algorithm = get_algorithm(learning_algo)
        self._table_hash = build_table(all_names)
        self._tokens = self._all_names[:self._num_tok]
        self.model = self._train(self._get_training_data())

    def _get_training_data(self):
        """Builds and returns the feature sets for the algorithm"""
        #positive_data with contextual information
        featuresets = []
        # this comes in name --- context\n
        ptokens = self.contexts
        # using only the defined names we get "name --- name"
        just_toks = [jtok + "---" + jtok for jtok in self._tokens]
        # now we have name --- context concat with name --- name
        ptokens = ptokens + just_toks
        # let's make a generator instead...
        ptokens = (x for x in ptokens if x != '')
        for tok in ptokens:
            name, context = tok.split("---", 1)
            context_array = nltk.word_tokenize(context.strip())
            name_parts = nltk.word_tokenize(name.strip())
            try:
                index = context_array.index(name_parts[0])
            except ValueError:
                index = 0
            span = len(name_parts) - 1
            featuresets.append((self.taxon_features(name, context_array,
                                index, span), 'taxon'))
            if(len(name_parts[0]) > 1 and name_parts[0][1] != "."):
                abb_name = name_parts[0][0] + ". " + " ".join(name_parts[1:])
                featuresets.append((self.taxon_features(abb_name,
                                    context_array, index, span), 'taxon'))
        #negative data
        ntokens = nltk.word_tokenize(self.irrelevant_text)
        # we want an iterator, not a list
        neg_trigrams = nltk.itrigrams(ntokens)
        # incrementer
        inx = -1
        # trigram count
        trigram_count = 0
        for p, q, r in neg_trigrams:
            if(trigram_count > self._num_neg_tg):
                break
            inx += 1
            trigram = p + " " + q + " " + r
            bigram = p + " " + q
            # It's looking for 'Something like'
            if(p[0].isupper() and p[1:].islower() and q.islower()):
                featuresets.append((self.taxon_features(bigram, ntokens, inx,
                                    1), 'not-a-taxon'))
                featuresets.append((self.taxon_features(p, ntokens, inx, 0),
                                    'not-a-taxon'))
                # It's looking for 'Something like this'
                if(r.islower()):
                    trigram_count += 1
                    featuresets.append((self.taxon_features(trigram, ntokens,
                                        inx, 2), 'not-a-taxon'))
            # this is looking for 'something Like this'
            if(q[0].isupper() and q[1:].islower()):
                featuresets.append((self.taxon_features(q, ntokens, inx + 1,
                                    0), 'not-a-taxon'))
            # this is looking for 'something like This'
            if(r[0].isupper() and r[1:].islower()):
                featuresets.append((self.taxon_features(r, ntokens, inx + 2,
                                    0), 'not-a-taxon'))
        random.shuffle(featuresets)
        return featuresets

    def taxon_features(self, token, context_array, index, span):
        """Returns a dictionary of features"""
        token = token.strip()
        # a now partially populated features dictionary
        features, string_weight = get_basic_features(token)
        # is the 3-word-token we have in the predefined list of species?
        # these features are the only ones that depend on the object
        features["word_1_in_table"] = (features["word_1"].lower() in 
                                       self._table_hash)
        features["word_2_in_table"] = (features["word_2"].lower() in
                                       self._table_hash)
        features["word_3_in_table"] = (features["word_3"].lower() in
                                       self._table_hash)
        # context span has and always will be 1
        features["%s_context" % (1)] = context_array[index + span + 1][0]
        if(index - 1 < 0):
            features["%s_context" % (-1)] = 'Null'
        else:
            features["%s_context" % (-1)] = context_array[index - 1][0]
        return features

    def _train(self, featuresets):
        """This trains the nltk model with the built featuresets.

        Arguments:
        featuresets --

        """
        return self.algorithm(featuresets)
