import nltk
import random
import re
import os
from neti_neti_helper import striptok

class NetiNetiTrainer:
    """A class that defines the training algorithm and the training files
    and actually trains a natrual language toolkit object (nltk)
    """
    def __init__(self, positive_training_file = "data/New_sp_contexts.txt",
                 negative_training_file = "data/pictorialgeo.txt",
                 sci_names_file = "data/millionnames.txt", learning_algorithm="NB",
                 sci_names_training_num = 10000, negative_trigrams_num = 5000, context_span=1):
        # TODO Too many arguments, perhaps create a TrainingFiles Class?
        """Builds and trains the NetiNeti model

        Keyword arguments:
        positive_training_file -- text with scientific names and a text that contains them (default "data/New_sp_contexts.txt")
        negative_training_file -- text without scientific names (default "data/pictorialgeo.txt")
        sci_names_file -- text containing only scientific names -- one name per line (default "data/millionnames.txt")
        learning_algorithm -- the algorithm to train with (default "Naive Bayesian: NB")
        sci_names_training_num -- number of scientific names from sci_names_file to use for training (default 10000)
        negative_trigrams_num -- number of negative trigrams to build for training (default 5000)
        context_span -- number of surrounding words from either side to use for context training (default 1)

        """
        self._positive_training_file = positive_training_file
        self._negative_training_file = negative_training_file
        self._sci_names_training_num = sci_names_training_num
        self._negative_trigrams_num = negative_trigrams_num
        self._context_span = context_span
        self._sci_names_file = sci_names_file
        self.learning_algorithm = learning_algorithm

        self._sci_names, self._white_list = self._tokenize_sci_names()
        featuresets = self._get_training_data()
        self._train_classifier(featuresets)

    def _tokenize_sci_names(self):
        """Returns a list of random scientific names and a dictionary of
        one-word tokens generated from the scientific names.

        Scientific names are supplied in an external file which has
        several million names, one name per line.

        The collection of tokens derived from those names is stored as a
        dictionary to ensure uniqueness of all tokens and to ensure
        fast access to them. Tokens stored as keys of the dictionary,
        values are irrelevant and are set to 1.
        """
        lines = open(self._sci_names_file).readlines()
        all_sci_names = [line.strip() for line in lines]
        random.shuffle(all_sci_names)
        sci_names = all_sci_names[:self._sci_names_training_num]
        white_list = {}
        for sci_name in all_sci_names:
            words = sci_name.split(" ") #TODO after refactoring: change to split() to avoid empty token. Then figure out how to eliminate empty token from other places
            for word in words:
                white_list[word.lower()] = 1
        return sci_names, white_list

    def _get_training_data(self):
        """Builds and returns positive and negative feature sets for the algorithm"""

        positive_training_data = self._get_positive_training_data()
        featuresets = self._get_positive_featuresets(positive_training_data)
        featuresets += self._get_negative_featuresets()
        return featuresets

    def _get_negative_featuresets(self):
        featuresets = []
        ndata = open(os.path.dirname(os.path.realpath(__file__)) + "/" +
                     self._negative_training_file).read()
        ntokens = nltk.word_tokenize(ndata)
        neg_trigrams = nltk.trigrams(ntokens)
        index = -1
        bigram_count = 0
        trigram_count = 0
        for first_word, second_word, third_word in neg_trigrams:
            if(trigram_count > self._negative_trigrams_num):
                break
            index += 1
            trigram = first_word + " " + second_word + " " + third_word
            bigram = first_word + " " + second_word
            if(first_word[0].isupper() and first_word[1:].islower() and second_word.islower()):
                bigram_count += 1
                featuresets.append((self.taxon_features(bigram, ntokens, index, 1),
                                    'not-a-taxon'))
                featuresets.append((self.taxon_features(first_word, ntokens, index, 0),
                                    'not-a-taxon')) #TODO find out if it makes sense to move it as a separate if statement
                if(third_word.islower()):
                    trigram_count += 1
                    featuresets.append((self.taxon_features(trigram, ntokens,
                                        index, 2), 'not-a-taxon'))
            #TODO after refactoring: it might make sense to generate unigram once, looks like we have duplicated unigrams here
            if(second_word[0].isupper() and second_word[1:].islower()):
                featuresets.append((self.taxon_features(second_word, ntokens, index + 1,
                                    0), 'not-a-taxon'))
            if(third_word[0].isupper() and third_word[1:].islower()):
                featuresets.append((self.taxon_features(third_word, ntokens, index + 2,
                                    0), 'not-a-taxon'))
        random.shuffle(featuresets)
        print("bigram trigram negative features: ", bigram_count + trigram_count)
        print("total examples: ", len(featuresets))
        return(featuresets)

    def _get_positive_training_data(self):
        """Returns list of data for positive training"""
        data = []
        for line in open(self._positive_training_file):
            if line.strip(): name, context = line.split("---", 1)
            data.append({ 'name' : name.strip(), 'context' : context.strip() })
        for sci_name in self._sci_names:
            if sci_name: data.append({ 'name' : sci_name, 'context' : sci_name })
        return data

    def _get_positive_featuresets(self, positive_training_data):
        """

        """
        featuresets = []
        for data in positive_training_data:
            name = data['name']
            context = data['context']
            context_tokens = nltk.word_tokenize(context)
            name_tokens = nltk.word_tokenize(name)
            try:
                index = context_tokens.index(name_tokens[0])
            except ValueError:
                index = 0 #TODO after refactoring: should index be 0 or it should be -1 or something?
            span = len(name_tokens) - 1

            features = self.taxon_features(name, context_tokens, index, span)
            featuresets.append((features, 'taxon'))

            # create abbreviated version of the name (e.g. Aus bus -> A. bus) and make features.
            if(len(name_tokens[0]) > 1 and name_tokens[0][1] != "."):
                abbr_name = name_tokens[0][0]+". " + " ".join(name_tokens[1:])
                features = self.taxon_features(abbr_name, context_tokens, index,span)
                featuresets.append((features, 'taxon'))
        return featuresets


    def _populateFeatures(self, array, idx, start, stop, features, name):
        # TODO change method to _populate_features
        # TODO catch a less general Exception
        # TODO could remove method from the class
        """Return a dictionary of features

        Arguments:
        array --
        idx -- index
        start --
        stop --
        features --
        name --
        """
        try:
            if(stop == "end"):
                features[name] = array[idx][start:]
            elif(stop == "sc"):
                features[name] = array[idx][start]
            else:
                features[name] = array[idx][start:stop]
        except Exception:
            features[name] = 'Null'
        return(features[name])

    def _incWeight(self, st_wt, inc, val):
        # TODO change name to _inc_weight
        # TODO change argument names to something useful
        # TODO could remove method from the class
        """O_o

        Arguments:
        st_wt -- starting weight?
        inc -- the amount to increase the starting weight?
        val -- maybe a boolean?
        """
        if(val):
            return(st_wt + inc)
        else:
            return(st_wt)

    def taxon_features(self, token, context_array, index, span):
        # TODO it's long. Perhaps split into several functions?
        # TODO change variable names, at least sv and c and probably others
        # TODO catch a less generic exception
        """Returns a dictionary of features"""
        token = token.strip()
        context_span = self._context_span
        features = {}
        swt = 5 # Weight Increment
        vowels = ['a', 'e', 'i', 'o', 'u']
        sv = ['a', 'i', 's', 'm']#last letter (LL) weight
        sv1 = ['e', 'o']# Reduced LL weight
        svlb = ['i', 'u']# penultimate L weight
        string_weight = 0
        prts = token.split(" ")
        #lc = self._populateFeatures(prts,0,-1,"sc",features,"last_char")
        #prts = [striptok(pt) for pt in prts]
        #if(lc =="."):
        #       prts[0] = prts[0]+"."
        self._populateFeatures(prts, 0, -3, "end", features, "last3_first")
        self._populateFeatures(prts, 1, -3, "end", features, "last3_second")
        self._populateFeatures(prts, 2, -3, "end", features, "last3_third")
        self._populateFeatures(prts, 0, -2, "end", features, "last2_first")
        self._populateFeatures(prts, 1, -2, "end", features, "last2_second")
        self._populateFeatures(prts, 2, -2, "end", features, "last2_third")
        self._populateFeatures(prts, 0, 0, "sc", features, "first_char")
        self._populateFeatures(prts, 0, -1, "sc", features, "last_char")
        self._populateFeatures(prts, 0, 1, "sc", features, "second_char")
        self._populateFeatures(prts, 0, -2, "sc", features, "sec_last_char")
        features["lastltr_of_fw_in_sv"] = j = self._populateFeatures(prts, 0,
            -1, "sc", features, "lastltr_of_fw_in_sv") in sv
        string_weight = self._incWeight(string_weight, swt, j)
        features["lastltr_of_fw_in_svl"] = j = self._populateFeatures(prts, 0,
            -1, "sc", features, "lastltr_of_fw_in_svl") in sv1
        string_weight = self._incWeight(string_weight, swt - 3, j)
        features["lastltr_of_sw_in_sv"] = j = self._populateFeatures(prts, 1,
            -1, "sc", features, "lastltr_of_sw_in_sv") in sv
        string_weight = self._incWeight(string_weight, swt, j)
        features["lastltr_of_sw_in_svl"] = j = self._populateFeatures(prts, 1,
            -1, "sc", features, "lastltr_of_sw_in_svl") in sv1
        string_weight = self._incWeight(string_weight, swt - 3, j)
        features["lastltr_of_tw_in_sv_or_svl"] = j = self._populateFeatures(
        prts, 2, -1, "sc", features, "lastltr_of_tw_in_sv_or_svl") in sv + sv1
        string_weight = self._incWeight(string_weight, swt - 2, j)
        features["2lastltr_of_tw_in_sv_or_svl"] = self._populateFeatures(prts,
            2, -2, "sc", features, "2lastltr_of_tw_in_sv_or_svl") in sv + sv1
        features["last_letter_fw_vwl"] = prts[0][-1] in vowels
        features["2lastltr_of_fw_in_sv"] = j = self._populateFeatures(prts,
            0, -2, "sc", features, "2lastltr_of_fw_in_sv") in sv
        features["2lastltr_of_fw_in_sv1"] = j = self._populateFeatures(prts,
            0, -2, "sc", features, "2lastltr_of_fw_in_sv1") in sv1
        features["2lastltr_of_fw_in_svlb"] = j = self._populateFeatures(prts,
            0, -2, "sc", features, "2lastltr_of_fw_in_svlb") in svlb
        features["2lastltr_of_sw_in_sv"] = j = self._populateFeatures(prts,
            1, -2, "sc", features, "2lastltr_of_fw_in_sv") in sv
        features["2lastltr_of_sw_in_sv1"] = j = self._populateFeatures(prts,
            1, -2, "sc", features, "2lastltr_of_sw_in_sv1") in sv1
        features["2lastltr_of_sw_in_svlb"] = j = self._populateFeatures(prts,
            1, -2, "sc", features, "2lastltr_of_fw_in_svlb") in svlb
        features["first_in_table"] = self._white_list.has_key(
            self._populateFeatures(prts, 0, 0, "end", features,
                                   "first_in_table").lower())
        features["second_in_table"] = self._white_list.has_key(
            self._populateFeatures(prts, 1, 0, "end", features,
                                   "second_in_table").lower())
        features["third_in_table"] = self._white_list.has_key(
            self._populateFeatures(prts, 2, 0, "end", features,
                                   "third_in_table").lower())
        #context_R = []
        #context_L = []
        for c in range(context_span):
            item = striptok(self._populateFeatures(
                context_array, index + span + c + 1, 0, "end", features,
                str(c + 1) + "_context"))
            #features[str(c+1)+"_context"] = self._populateFeatures(
            #    context_array,index+span+c+1,0,"end",
            #    features,str(c+1)+"_context").strip()
            features[str(c + 1) + "_context"] = item
            if(index + c - context_span < 0):
                features[str(c - context_span) + "_context"] = 'Null'
            else:
                item1 = striptok(self._populateFeatures(
                    context_array, index + c - context_span, 0, "end",
                    features, str(c - context_span) + "_context"))
#               features[str(c-context_span)+"_context"] =
#                   self._populateFeatures(context_array,index+c-context_span,
#                   0,"end",features,str(c-context_span)+"_context").strip()
                features[str(c - context_span) + "_context"] = item1
#                R = features[str(1)+"_context"]
#                L = features[str(-1)+"_context"]
#                if( L =="Null"):
#                        features["pos_tag"+str(-1)+"_context"] = "UKNWN"
#                else:
#                        features["pos_tag"+str(-1)+"_context"] =
#                       nltk.pos_tag([features[str(-1)+"_context"]])[0][1]
#
#                if( R =="Null"):
#                        features["pos_tag"+str(1)+"_context"] = "UKNWN"
#                else:
#                        features["pos_tag"+str(1)+"_context"] =
#                       nltk.pos_tag([features[str(1)+"_context"]])[0][1]
#       features["pos_tag"+str(1)+"_context"] =
#           nltk.pos_tag([features[str(1)+"_context"]])[0][1]
#       features["pos_tag"+str(-1)+"_context"] =
#           nltk.pos_tag([features[str(-1)+"_context"]])[0][1]
        try:
            features["1up_2_dot_restok"] = (token[0].isupper() and
                                            token[1] is "." and
                                            token[2] is " " and
                                            token[3:].islower())
        except Exception:
            features["1up_2_dot_restok"] = False
        features["token"] = token
        for vowel in'aeiou':
            features["count(%s)" % vowel] = token.lower().count(vowel)
            features["has(%s)" % vowel] = vowel in token
        imp = token[0].isupper() and token[1:].islower()
        if(string_weight > 18):
            features["Str_Wgt"] = 'A'
        elif(string_weight >14):
            features["Str_Wgt"] = 'B'
        elif(string_weight > 9):
            features["Str_Wgt"] = 'C'
        elif(string_weight > 4):
            features["Str_Wgt"] = 'D'
        else:
            features["Str_Wgt"] = 'F'
        features["imp_feature"] = imp
        return features

    def _train_classifier(self, featuresets):
        # TODO nltk doesn't have MaxentClassifier, probably MaxEntClassifier
        # TODO define self._model in the __init__ method
        """This changes the algorithm that nltk uses to train the model.

        Arguments:
        featuresets -- array of features generated for training

        """
        model = None
        if(self.learning_algorithm == "NB"):
            model = nltk.NaiveBayesClassifier.train(featuresets)
        elif(self.learning_algorithm == "MaxEnt"):
            model = nltk.MaxentClassifier.train(featuresets, "MEGAM",
                                                 max_iter=15)
        elif(self.learning_algorithm == "DecisionTree"):
            model = nltk.DecisionTreeClassifier.train(featuresets, 0.05)
        self._model = model

    def get_model(self):
        """An accessor method for the model."""
        return self._model

