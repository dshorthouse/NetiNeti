# Machine Learning based approach to find scientific names
# Input: Any text preferably in Engish
# Output : A list of scientific names

"""
netineti.py

Created by Lakshmi Manohar Akella.
Updated on October 27 2010 (ver 0.945).
Copyright (c) 2010, Marine Biological Laboratory. All rights resersved.

"""
import time
import nltk
import random
import re
import os

#import psyco

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
        irrelevant_text -- describe arg (default "data/pictorialgeo.txt")
        all_names -- describe arg (default "data/millionnames.txt")
        learning_algo -- the algorithm to train with (default "NB")
        num_tok_train -- number of tokens to train on? (default 10000)
        num_neg_tg -- describe arg (default 5000)
        context_span -- describe arg (default 1)

        """
        self._clnr = TextClean()
        self.species_train = species_train
        self.irrelevant_text = irrelevant_text
        self._num_tok = num_tok_train
        self._num_neg_tg = num_neg_tg
        self._context_span = context_span
        self._all_names = all_names
        self.learning_algo = learning_algo
        #psyco.bind(self._getTrainingData)
        #psyco.bind(self.taxon_features)
        self._buildTable()
        self._buildFeatures(self._getTrainingData())

    def _splitGet(self, fileName):
        """Takes name of a file, and returns back a list where every element
        is a one line from the file, clenaed from trailing whitespaces..

        This method is used to return a list of scientific names taken from a
        text file whih contains name per line.

        """
        # TODO change the method to _split_get(self, file_name)
        # TODO .split('\n') should be .splitlines()
        # TODO map is superseeded by list comprehension
        # TODO could remove method from the class
        """Return a list of the lines of the input file.

        Arguments:
        fileName -- the file to read

        """
        pdata = open(os.path.dirname(os.path.realpath(__file__)) + "/"  + fileName).read()
        tokens = pdata.split('\n')
        #remove trailing spaces
        tokens = map(lambda x:x.strip(), tokens)
        return(tokens)

    def _getTrainingData(self):
        # TODO Too many local variables, perhaps make this several methods?
        # TODO rename _getTrainingData to _get_training_data
        # TODO filter can be replaced by list comprehension
        # TODO We should catch a better Exception
        # TODO Rename the variables: p, q, r, tg, bg
        """Builds and returns the feature sets for the algorithm"""
        #positive_data with contextual information
        featuresets = []
        ptokens = self._splitGet(self.species_train)
        print("Number of contexts: ", len(ptokens))
        just_toks = [jtok + "---" + jtok for jtok in self._tokens]
        print("Number of toks: ", len(just_toks))
        ptokens = ptokens + just_toks
        ptokens = filter(lambda x: len(x) > 0, ptokens)
        print("train toks: ", len(ptokens))
        for tok in ptokens:
            name, context = tok.split("---", 1)
            context_array = nltk.word_tokenize(context.strip())
            name_parts = nltk.word_tokenize(name.strip())
            try:
                index = context_array.index(name_parts[0])
            except Exception:
                index = 0
            span = len(name_parts) - 1
            featuresets.append((self.taxon_features(name, context_array,
                                index,span), 'taxon'))
            if(len(name_parts[0]) > 1 and name_parts[0][1] != "."):
                abb_name = name_parts[0][0]+". " + " ".join(name_parts[1:])
                featuresets.append((self.taxon_features(abb_name,
                                    context_array, index,span), 'taxon'))
        print("# pos features.. ", len(featuresets))
        #negative data
        ndata = open(os.path.dirname(os.path.realpath(__file__)) + "/" +
                     self.irrelevant_text).read()
        ntokens = nltk.word_tokenize(ndata)
        neg_trigrams = nltk.trigrams(ntokens)
        print("trigrams: ", len(neg_trigrams))
        inx = -1
        bgc = 0
        tgc = 0
        print("Building neg features")
        for p, q, r in neg_trigrams:
            if(tgc > self._num_neg_tg):
                break
            inx += 1
            tg = p + " " + q + " " + r
            bg = p + " " + q
            if(p[0].isupper() and p[1:].islower() and q.islower()):
                bgc += 1
                featuresets.append((self.taxon_features(bg, ntokens, inx, 1),
                                    'not-a-taxon'))
                featuresets.append((self.taxon_features(p, ntokens, inx, 0),
                                    'not-a-taxon'))
                if(r.islower()):
                    tgc += 1
                    featuresets.append((self.taxon_features(tg, ntokens,
                                        inx, 2), 'not-a-taxon'))
            if(q[0].isupper() and q[1:].islower()):
                featuresets.append((self.taxon_features(q, ntokens, inx + 1,
                                    0), 'not-a-taxon'))
            if(r[0].isupper() and r[1:].islower()):
                featuresets.append((self.taxon_features(r, ntokens, inx + 2,
                                    0), 'not-a-taxon'))
        random.shuffle(featuresets)
        print("bg tg negative features: ", bgc + tgc)
        print("total examples: ", len(featuresets))
        return(featuresets)

    def _buildTable(self):
        # TODO rename method to _build_table
        # TODO Do we really need to time this?
        # TODO rename ta, t, p, tb to something useful
        # TODO remove print statements
        # TODO move creation of _tab_hash and _tokens to the __init__ method
        """Creates a collection of one-word tokens generated from
        a ranomized subset of scientific names. Scientific names are supplied from an
        external file which has several millions of names. This collection of tokens
        is stored as a dictionary to ensure uniqueness of all the tokens and make a
        fast access to them. Tokens stored as keys of the dictionary, values are
        irrelevant and are set to 1.

        The collection is stored in as an instance variable.

        Used variables:

        self._all_names -- full list of all scientific names
        self._num_tok   -- number of

        """
        ta = time.clock()
        ttokens = self._splitGet(self._all_names)
        random.shuffle(ttokens)
        self._tokens = ttokens[:self._num_tok]
        self._tab_hash = {}
        for t in ttokens:
            prts = t.split(" ")
            for p in prts:
                self._tab_hash[p.lower()] = 1
        tb = time.clock()
        print(str(tb - ta))
        print(len(self._tab_hash))

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
        #prts = [self._clnr.striptok(pt) for pt in prts]
        #if(lc =="."):
        #       prts[0] = prts[0]+"."

        # This relies on side effects of the method. NO NO NO NO NO
        # this gets the "last three characters of the first word"
        self._populateFeatures(prts, 0, -3, "end", features, "last3_first")
        # this gets the "last three characters of the second word"
        self._populateFeatures(prts, 1, -3, "end", features, "last3_second")
        # this gets the "last three characters of the third word"
        self._populateFeatures(prts, 2, -3, "end", features, "last3_third")
        self._populateFeatures(prts, 0, -2, "end", features, "last2_first")
        self._populateFeatures(prts, 1, -2, "end", features, "last2_second")
        self._populateFeatures(prts, 2, -2, "end", features, "last2_third")
        # pretty sure sc = single character
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
        features["first_in_table"] = self._tab_hash.has_key(
            self._populateFeatures(prts, 0, 0, "end", features,
                                   "first_in_table").lower())
        features["second_in_table"] = self._tab_hash.has_key(
            self._populateFeatures(prts, 1, 0, "end", features,
                                   "second_in_table").lower())
        features["third_in_table"] = self._tab_hash.has_key(
            self._populateFeatures(prts, 2, 0, "end", features,
                                   "third_in_table").lower())
        #context_R = []
        #context_L = []
        for c in range(context_span):
            item = self._clnr.striptok(self._populateFeatures(
                context_array, index + span + c + 1, 0, "end", features,
                str(c + 1) + "_context"))
            #features[str(c+1)+"_context"] = self._populateFeatures(
            #    context_array,index+span+c+1,0,"end",
            #    features,str(c+1)+"_context").strip()
            features[str(c + 1) + "_context"] = item
            if(index + c - context_span < 0):
                features[str(c - context_span) + "_context"] = 'Null'
            else:
                item1 = self._clnr.striptok(self._populateFeatures(
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

    def _buildFeatures(self, featuresets):
        # TODO change name to _build_features
        # TODO change at least NB and MaxEnt variables, probably others
        # TODO nltk doesn't have MaxentClassifier, probably MaxEntClassifier
        # TODO define self._model in the __init__ method
        # TODO remove print statements
        """This changes the algorithm that nltk uses to train the model.

        Arguments:
        featuresets --

        """
        if(self.learning_algo == "NB"):
            #WNB = nltk.classify.weka.WekaClassifier.train("Naive_Bayes_weka",
            #featuresets,"naivebayes")
            NB = nltk.NaiveBayesClassifier.train(featuresets)
            self._model = NB
        elif(self.learning_algo == "MaxEnt"):
            print("MaxEnt")
            MaxEnt = nltk.MaxentClassifier.train(featuresets, "MEGAM",
                                                 max_iter=15)
            #DT = nltk.DecisionTreeClassifier.train(featuresets)
            self._model = MaxEnt
        elif(self.learning_algo == "DecisionTree"):
            print("Decision Tree is learning")
            DTree = nltk.DecisionTreeClassifier.train(featuresets, 0.05)
            self._model = DTree

    def getModel(self):
        # TODO change name to get_model
        """An accessor method for the model."""
        return self._model

class NameFinder():
    """The meat of NetiNeti. This class uses the trained NetiNetiTrain model
    and searches through text to find names.

    This version supports offsets.

    """

    def __init__(self, modelObject, e_list='data/new-list.txt'):
        # TODO change the name of modelObject to model_object
        # TODO change the variables e_list, a and reml to something useful
        """Create the name finder object.

        Arguments:
        modelObject -- maybe the trained NetiNetiTrain object?

        Keyword Arguments:
        e_list -- describe argument (default "data/new-list.txt")

        """
        reml = {}
        elist = open(os.path.dirname(os.path.realpath(__file__)) + "/"  +
                     e_list).read().split("\n")
        for a in elist:
            reml[a] = 1
        self._remlist = reml
        self._modelObject = modelObject
        self._clnr = TextClean()
        #psyco.bind(self.findNames)
        #psyco.bind(self.find_names)

    def _remDot(self, a):
        # TODO change the name to _remove_dot (or something similar)
        # TODO change the variable 'a' to something useful
        # TODO could remove method from the class
        """Return the string with no dot at the end of it.

        removes period from words that are not an obvious genus abbreviaion
        sometimes people abbreviate genus to 2 or 3 letters, would it be a problem?
        we assume here that abbr is almost alwqys 1 letter

        Arguments:
        a -- token, usually the first element of a trigram

        """
        if(len(a) > 2 and a[-1] == '.'):
            return(a[:-1])
        else:
            return (a)

    def _hCheck(self, a):
        # TODO change name to something useful, not _h_check
        # TODO change variables (a, w, j, e1) to something useful
        """Returns a boolean.
        checks if a word is in a black list

        Arguments:
        a -- a token, first element of a trigram

        """
        a = self._remDot(a)
        e1 = a.split("-")
        j = [self._remlist.has_key(w) for w in e1]
        return(not True in j and not self._remlist.has_key(a.lower()))

    def _isGood2(self, a, b):
        # TODO change name to something useful, not _is_good_2
        # TODO change variable names (a, b, td, s1) to something useful
        """Returns a boolean.
        Checks if a bigram looks right

        Arguments:
        a -- first element of a bigram or a trigram
        b -- second element of a bigram or a trigram

        """
        if(len(a) > 1 and len(b) > 1):
            td = (a[1] == '.' and len(a) ==2)
            s1 = a[0].isupper() and b.islower() and ((a[1:].islower() and
                a.isalpha()) or td) and (self._remDot(b).isalpha() or '-' in b)
            return(s1 and self._hCheck(a) and self._hCheck(b))
        else:
            return(False)

    def _isGood3(self, a, b, c):
        # TODO change name to something useful, not _is_good_3
        # TODO change variable names to something useful
        #      including a, b, c, s1, b_par_exp, s2
        """Returns a boolean.
        Checks if a trigram looks right

        Arguments:
        a -- first element of a trigram
        b -- second element of a trigram
        c -- third element of a trigram

        """
        if(len(a) > 1 and len(b) > 1 and len(c) > 1):
            s1 = c.islower() and self._remDot(c).isalpha()
            b_par_exp = b[0] + b[-1] == "()"
            if(b_par_exp):
                s2 = b[1].isupper() and ((b[2] == "." and len(b) == 4) or
                                        b[2:-1].islower() and
                                        b[2:-1].isalpha()) and b[-1] != "."
                return(s1 and self._hCheck(c) and s2 and (a[0].isupper() and
                                                         ((a[1] == "." and
                                                           len(a) == 2) or
                                                          a[1:].islower() and
                                                          a.isalpha())))
            else:
                return(s1 and self._isGood2(a, b) and self._hCheck(c))
        elif(len(a) > 1 and len(b) == 0 and len(c) > 1):
            return(self._isGood2(a, c))
        else:
            return(False)

    def _taxonTest(self, tkn, context, index, span):
        # TODO rename to _taxon_test or similar
        # TODO change some of the variables names to something useful
        # TODO perhaps make this more than one line?
        """Test for a taxon

        Arguments:
        tkn -- token?
        context -- describe argument
        index -- describe argument
        span -- describe argument

        """
        return((self._modelObject.getModel().classify(
            self._modelObject.taxon_features(tkn, context, index, span)) ==
            'taxon'))

    def _resolve(self, a, b, c, nhash, nms, last_genus, plg):
        # TODO change all variable names to something useful
        # TODO programming challenge! you only need to call remDot on c since
        #  it only affects the last letter in the string
        """

        Arguments:
        a -- describe argument
        b -- describe argument
        c -- describe argument
        nhash -- describe argument
        nms -- describe argument
        last_genus -- describe argument
        plg -- describe argument

        """
        #gr =self._remDot((a+" "+b+" "+c).strip())
        if(b == ""):
            gr = self._remDot((a + " " + c).strip())
        else:
            gr = self._remDot((a + " " + b + " " + c).strip())
        if(gr[1] == "." and gr[2] == " "):
            if(nhash.has_key(gr)):
                nms.append(self._remDot((a[0] + "[" + nhash[gr] + "]" + " " +
                                        b + " " + c).strip()))
            elif(last_genus and a[0] == last_genus[0]):
                nms.append(self._remDot((a[0] + "[" + last_genus[1:] + "]" +
                                        " " + b + " " + c).strip()))
            elif(plg and a[0] == plg):
                nms.append(self._remDot((a[0] + "[" + plg[1:] + "]" + " " +
                                        b + " " + c).strip()))
            else:
                nms.append(gr)
        else:
            nms.append(gr)
            nhash[self._remDot((a[0] + ". " + b + " " + c).strip())] = a[1:]

    def find_names(self, text, resolvedot=False):
        # TODO fix variable names
        # TODO perhaps break this up into smaller functions
        """Return a string of names concatenated with a newline and a list of
        offsets for each mention of the name in the original text.

        Arguments:
        text -- input text

        Keyword Arguments:
        resolvedot -- boolean to resolve full name of a genus (false by default) and not
                      recommended for use
        """
        self._text = text
        #tok = nltk.word_tokenize(text)
        #tok = nltk.sexpr_tokenize(text)
        #text = re.sub('\n|\{|\}|,|"'," ",text)
        tok = text.split(" ")
        #tok = [b for a in tok for b in a.split("\t")]
        tok = [b for a in tok for b in a.split("\n")]
        names, newnames, offsets = self.findNames(tok)
        sn = set(names)
        lnames = list(sn)
        rnames = []
        nh = {}
        if(resolvedot):
            abrn = [a for a in lnames if(a[1] == "." and a[2] == " ")]
            diff = sn.difference(set(abrn))
            ld = list(diff)
            for i in ld:
                prts = i.split(" ")
                st = " ".join(prts[1:])
                nh[i[0] + ". " + st] = prts[0][1:]
            nl = []
            for n in abrn:
                if(nh.has_key(n)):
                    nl.append(n[0] + "[" + nh[n] + "]" + " " + n[3:])
                else:
                    nl.append(n)
            resolved_list = nl + ld
            resolved_list.sort()
            rnames = resolved_list
        else:
            lnames.sort()
            rnames = lnames
        return("\n".join(rnames), newnames, offsets)

    def _cleanTok(self, a, b, c):
        # TODO rename method to _clean_tokens or similar
        # TODO rename variables (a, b, c, a1, b1, ra, rb)
        """Cleans the tokens.
        Intelligent strip of trigram parts

        Arguments:
        a -- first element of a trigram
        b -- second element of a trigram
        c -- third element of a trigram

        """
        a1, b1 = a.strip(), b.strip()
        ra, rb = a1, b1
        if((len(a1) > 1)):
            if(a1[-1] == "."):
                ra = self._clnr.leftStrip(a1)[0]
            else:
                ra = self._clnr.striptok(a1)
        if(len(b1) > 1):
            if(b1[0] + b1[-1] == "()"):
                pass
            elif(b1[-1] == "-"):
                rb = self._clnr.leftStrip(b1)[0]
            else:
                rb = self._clnr.striptok(b1)
        return(ra, rb, self._clnr.striptok(c))

    def _createIndex(self, token):
        # TODO rename method to _create_index or similar
        # TODO there is lots of programming cleanup that can happen here
        # TODO rename variables, specifically oh
        # TODO could remove method from the class
        """Returns a dictionary indexes for all tockens. Key is a token number in
        the document, Value is the length of the token.

        Arguments:
        token -- list of all tokens from the document checked for scientific names

        """
        length = 0
        oh = {}
        for i in range(len(token)):
            if(i == 0):
                oh[i] = 0
            else:
                oh[i] = length
            length = length + len(token[i]) + 1 #or delim length
        return(oh)

    def _getOffsets(self, oh, index, a, b, c):
        # TODO rename method to _get_offsets
        # TODO rename variables (oh, a, b, c, st)
        # TODO could remove method from the class
        """Returns a tuple with start and end positions of a found scientific name.

        Arguments:
        oh -- a dictionary containing number of tokens as keys, and corresponding starting position
        of a token in the document agaist whih neti-neti runs as a value
        index -- index of the first token from the found scientific name.
        a -- first element of a trigram
        b -- second element of a trigram
        c -- third element of a trigram
        """
        st = a + " " + b + " " + c
        st = st.strip()
        return oh[index], oh[index] + len(st)

    def _uninomialCheck(self, tok):
        # TODO rename method to _uninomial_check or similar
        # TODO rename variable tok to token
        # TODO since neither remdot nor h_check refer to the object
        #  neither does this method
        """Checks to see if a token is a uninomial and returns a boolean.

        This method currently only allows uninomials of size larger than 5,
        however there are uninomial which are 2 characters in size.

        Arguments:
        tok -- the token to check as a ponential uninomial
        """
        if(len(tok) > 5 and tok[0].isupper() and tok[1:].islower() and
            (self._remDot(tok).isalpha() or (tok[0].isupper() and
                                        tok[1] == "." and tok[2].islower() and
                                        self._remDot(tok[2:]).isalpha())) and
                                        self._hCheck(tok)):
            return(True)
        else:
            return(False)

    def _endingCheck(self, tok):
        # TODO rename method to _ending_check or similar
        # TODO this doesn't really use the object since remdot does not
        # TODO filter can be replaced with a list comprehension
        """Check the ending of the token. It returns True if token has an ending
        characteristic for a word from a canonical scientific name

        Arguments:
        tok -- the token to check
        """
        endings = ['aceae', 'ales', 'eae', 'idae', 'ina', 'inae', 'ineae',
                    'ini', 'mycetes', 'mycota', 'mycotina', 'oidea', 'oideae',
                    'opsida', 'phyceae', 'phycidae', 'phyta', 'phytin']
        if(len(filter(lambda x: self._remDot(tok.lower()).endswith(x),
                                            endings)) > 0):
            return(True)
        else:
            return(False)

    def findNames(self, token):
        # TODO find a new method name, we already have find_names
        # TODO perhaps split this into several variables?
        # TODO catch a less general exception
        # TODO pylint says too many branches, that should get fixed if we
        #  move this to separate functions
        # TODO rename all the variables. All of them. GAHHH
        """It returns this: return(nms, nnewn, nnofl).
        takes list of all tokens from a document and returns back tuple
        of found names. First element is a list of names, second -- names separated by
        a new line, third offsets for each mention of the name in the document

        Arguments:
        token -- list with all tokens from the document searched for scientific names

        """
        icount = -1 #index as we iterate over trigrams
        nms = [] # list for names
        last_genus = ""
        prev_last_genus = ""
        nhash = {}
        ts = time.clock()
        oh = self._createIndex(token)
        offset_list = []
        if(len(token) == 2):
            if(self._isGood2(token[0], token[1]) and self._taxonTest(token[0] +
                                                                    " " +
                                                                    token[1],
                                                                    token, 0,
                                                                    1)):
                nms.append(token[0] + " " + token[1])
        elif(len(token) == 1):
            if(len(token[0]) > 2 and token[0][0].isupper() and
                token[0].isalpha() and self._hCheck(token[0]) and
                self._taxonTest(token[0], token, 0, 0)):
                nms.append(token[0])
        else:
            tgr = nltk.trigrams(token)
            #not generating bigrams...getting them from trigrams..
            # little more efficient
            for a, b, c in tgr:
                icount += 1
                #print a,icount
                p, q, r = self._cleanTok(a, b, c)
                #p1,q1,r1 = a.strip(),b.strip(),c.strip()
                #print "p q r = ", p,"--",q,"--",r
                #print "p1,q1,r1 = ",p1,q1,r1
                bg = self._remDot(p + " " + q)
                tg = self._remDot(p + " " + q + " " + r)
                j = -1
                count = 0
                if(nms):
                    while(abs(j) <= len(nms)):
                        if(nms[j][1] != "[" and nms[j][1] != "."):
                            if(count == 0):
                                last_genus = nms[j].split(" ")[0]
                                count = count + 1
                            else:
                                prev_last_genus = nms[j].split(" ")[0]
                                break
                        j = j - 1
                if(self._isGood3(p, q, r)):
                    #print "good trigram ...."
                    if(self._taxonTest(tg, token, icount, 2)):
                        #print "passed trigram..."
                        start, end = self._getOffsets(oh, icount, a, b, c)
                        offset_list.append((start, end))
                        self._resolve(p, q, r, nhash, nms, last_genus,
                                      prev_last_genus)
                elif(self._isGood2(p, q)):
                    #print "good bigram..."
                    if(self._taxonTest(bg, token, icount, 1)):
                        #print "passed bigram..."
                        start, end = self._getOffsets(oh, icount, a, b, "")
                        offset_list.append((start, end))
                        self._resolve(p, q, "", nhash, nms, last_genus,
                                      prev_last_genus)
                elif(self._uninomialCheck(p)):
                    if(self._taxonTest(re.sub("\.", ". ", self._remDot(p)),
                                        token, icount, 0)):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(self._remDot(p))
                    elif(self._endingCheck(p)):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(self._remDot(p))
                elif(self._endingCheck(p)):
                    if(self._hCheck(p) and p[0].isupper() and
                        self._remDot(p).isalpha()):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(self._remDot(p))
        try:
            if(self._isGood2(tgr[-1][-2], tgr[-1][-1])):
                if(self._taxonTest(self._remDot(tgr[-1][-2] + " " +
                    tgr[-1][-1]), token, icount + 1, 1)):
                    self._resolve(tgr[-1][-2], tgr[-1][-1], "", nhash, nms,
                    last_genus, prev_last_genus)
                    #nms.append(self._remDot(tgr[-1][-2]+" "+tgr[-1][-1]))
                elif(self._uninomialCheck(tgr[-1][-2])):
                    if(self._taxonTest(re.sub("\.", " ",
                        self._remDot(tgr[-1][-2])), token, icount + 1, 0)):
                        nms.append(self._remDot(tgr[-1][-2]))
        except Exception:
            print ""
        te = time.clock()
        nnewn = []
        nnofl = []
        #print len(offset_list)
        for o in offset_list:
            nme = self._text[o[0]:o[1]]
            pts = nme.split(" ")
            if(pts[0][0] + pts[0][-1] == "()"):
                #print nme+"...."
                no1 = o[0]
                no2 = o[1] + self._clnr.rightStrip(nme)[1]
            else:
                #print nme
                #print "o1 ",o[0]
                #print "o2 ",o[1]
                #print "left strip...", self._clnr.leftStrip(nme)[1]
                #print "right strip...",self._clnr.rightStrip(nme)[1]
                #print "................."
                no1 = o[0] + self._clnr.leftStrip(nme)[1]
                no2 = o[1] + self._clnr.rightStrip(nme)[1]
            tj = self._text[no1:no2]
            nnewn.append(tj)
            nnofl.append((no1, no2))
        print (te - ts)
        #print len(nnewn)
        #print len(nnofl)
        return(nms, nnewn, nnofl)

    def embedNames(lst, filename):
        # TODO rename to embed_names or similar
        # TODO change variable names
        # TODO self should be first method argument
        """
        Used to create a text with randomly placed scientific names in it
        (perhaps for testing purposes).

        Note: such a text will not have context relevant to the embedded
        scientific names. I do not think this method is used anymore.

        Arguments:
        lst -- list of scientific names
        filename -- file name with a text

        """
        f = open(os.path.dirname(os.path.realpath(__file__)) + "/"  +
                filename).read()
        sents = nltk.sent_tokenize(f)
        tksents = [nltk.word_tokenize(a) for a in sents]
        #esents = tksents
        for l in lst:
            i = random.randint(0, len(tksents) - 1)
            tksents[i].insert(random.randint(0, len(tksents[i]) - 1), l)
        sents = [" ".join(t) for t in tksents]
        etext = " ".join(sents)
        return(etext)


class TextClean():
    # TODO create an __init__ method
    """This appears to be a class dedicated to cleaning text. There is much
    work to do.

    """

    def leftStrip(self, t):
        # TODO rename method
        # TODO rename variables
        """This takes a token and strips non alpha characters off the left. It
        returns the stripped string and the number of characters it stripped.

        Arguments:
        t -- a one word token which might have trailing non alpha characters

        """
        i = 0
        while(i < len(t)):
            if(not t[i].isalpha()):
                i = i + 1
            else:
                break
        if(i == len(t)):
            return('', 0)
        return(t[i:], i)

    # This strips non alpha characters from the right of a string
    # and returns the new string and the number of characters stripped negated
    def rightStrip(self, t):
        # TODO rename method
        # TODO rename variables
        """This takes a token and strips non alpha characters off the right. It
        returns the stripped string and the number of characters it stripped.

        amount of stripped characters allows to calculate locations of found
        scientific names within the original document

        Arguments:
        t -- a one word token

        """
        j = -1
        while(j >= -len(t)):
            if(not t[j].isalpha()):
                j = j - 1
            else:
                break
        if(j == -1):
            return(t, 0)
        elif(j == -(len(t) + 1)):
            return('', 0)
        else:
            return(t[:j + 1], j + 1)

    def striptok(self, t):

        # TODO rename method
        # TODO rename variables
        """This combines leftStrip and rightStrip into one method.
        Returns back token without trailing non alpha characters

        Arguments:
        t -- a one word token which might contain trailing non alpha characters
             like parentheses, comma, etc...

        """
        return(self.rightStrip(self.leftStrip(t)[0])[0])


#psyco.bind(NameFinder)
#psyco.bind(TextClean)
if __name__ == '__main__':
    print "NETI..NETI\n"
