
def left_strip(word):
    """This takes a token and strips non alpha characters off the left. It
    returns the stripped string and the number of characters it stripped.

    Arguments:
    word -- a one word token which might have trailing non alpha characters

    """
    i = 0
    while(i < len(word)):
        if(not word[i].isalpha()):
            i = i + 1
        else:
            break
    if(i == len(word)):
        return '', 0
    return word[i:], i

def right_strip(word):
    """This takes a token and strips non alpha characters off the right. It
    returns the stripped string and the number of characters it stripped.

    amount of stripped characters allows to calculate locations of found
    scientific names within the original document

    Arguments:
    word -- a one word token

    """
    i = -1
    while(i >= -len(word)):
        if(not word[i].isalpha()):
            i = i - 1
        else:
            break
    if(i == -1):
        return word, 0
    elif(i == -(len(word) + 1)):
        return '', 0
    else:
        return word[:i + 1], i + 1

def strip_token(word):
    """This combines leftStrip and rightStrip into one method.
    Returns back token without trailing non alpha characters

    Arguments:
    word -- a one word token which might contain trailing non alpha characters
            like parentheses, comma, etc...

    """
    return right_strip(left_strip(word)[0])[0]

def build_table(filename):
    """Creates a collection of one-word tokens generated from a ranomized 
    subset of scientific names. Scientific names are supplied from an external
    file which has several millions of names. This collection of tokens is 
    stored as a dictionary to ensure uniqueness of all the tokens and make a
    fast access to them. Tokens stored as keys of the dictionary, values are
    irrelevant and are set to 1.

    We are just going to use python's set data structure becasue this is 
    exactly what it's supposed to do...unique lists.

    The collection is stored in as an instance variable.

    Arguments:
    filename -- the name of the file to build a table out of

    """
    # let's use a set since we want a unique list
    names = set()
    lines = split_get(filenames)
    # we have to shuffle it, the interwebz said so
    lines = random.shuffle(lines)
    for line in lines:
        # get each individual word from each line
        for name in line.split(" "):
            # to build a set of unique words from a file
            names.add(name.lower())
    return names

def get_basic_features(sentence):
    """This function takes a three letter sentence and breaks it up into 3
    words and then builds a dictionary of features of the word.

    Arguments:
    stenence -- A trigram or bigram, usually e.g. Gorilla gorilla gorilla

    """
    features = {}
    letter_lists = {'sv': ['a', 'i', 's', 'm'],
            'sv1': ['e', 'o'],
            'svlb': ['i', 'u'],
            'vowels': ['a', 'e', 'i', 'o', 'u'],
    }
    names = sentence.split(" ")
    string_weight = 0
    # generate numbers and names (1, Gorilla), (2, gorilla), (3, gorilla)
    for i, name in enumerate(names, 1):
        word = "word_%s" % (i)
        # going to comment these out until I know they get used
        #features["%s_first_char" % word] = name[0]
        #features["%s_second_char" % word] = name[1]
        features["%s_last_char" % word] = name[-1]
        features["%s_second_to_last_char" % word] = name[-2]
        #features["%s_last_three_chars" % word] = name[-3:]
        #features["%s_last_two_chars" % word] = name[-2:]
    # just build the features by hand now, we can be clever later.
    features["word_1_last_char_in_vowels"] = features["word_1_last_char"] in letter_lists['vowels']
    features["word_1_last_char_in_sv"] = features["word_1_last_char"] in letter_lists['sv']
    features["word_1_last_char_in_sv1"] = features["word_1_last_char"] in letter_lists['sv1']
    features["word_1_second_to_last_char_in_sv"] = features["word_1_second_to_last_char"] in letter_lists['sv']
    features["word_1_second_to_last_char_in_sv1"] = features["word_1_second_to_last_char"] in letter_lists['sv1']
    features["word_1_second_to_last_char_in_svlb"] = features["word_1_second_to_last_char"] in letter_lists['svlb']
    features["word_2_last_char_in_sv"] = features["word_2_last_char"] in letter_lists['sv']
    features["word_2_last_char_in_sv1"] = features["word_2_last_char"] in letter_lists['sv1']
    features["word_2_second_to_last_char_in_sv"] = features["word_2_second_to_last_char"] in letter_lists['sv']
    features["word_2_second_to_last_char_in_sv1"] = features["word_2_second_to_last_char"] in letter_lists['sv1']
    features["word_2_second_to_last_char_in_svlb"] = features["word_2_second_to_last_char"] in letter_lists['svlb']
    features["word_3_last_char_in_vowels"] = features["word_3_last_char"] in letter_lists['vowels']
    features["word_3_last_char_in_sv_or_sv1"] = features["word_3_last_char"] in letter_lists['sv'] + letter_lists['sv1']
    features["word_3_second_to_last_char_in_sv_or_sv1"] = features["word_3_secont_to_last_char"] in letter_lists['sv'] + letter_lists['sv1']

    if (features["word_1_last_char_in_sv"]):
        string_weight = string_weight + 5
    if (features["word_1_last_char_in_sv1"]):
        string_weight = string_weight + 2
    if (features["word_2_last_char_in_sv"]):
        string_weight = string_weight + 5
    if (features["word_2_last_char_in_sv1"]):
        string_weight = string_weight + 2
    if (features["word_3_second_to_last_char_in_sv_or_sv1"]):
        string_weight = string_weight + 3
    # change string weight if
    # last letter of first word in sv        | 5
    # last letter of first wird in sv1       | 5 - 3
    # last letter of second word in sv       | 5
    # last letter of second word in sv1      | 5 - 3
    # last letter of third word in sv or sv1 | 5 - 2
    # vowels
    # last letter of first word in vowels?
    # sv
    # last letter of first word in sv
    # last letter of second word in sv
    # second to last letter of first word in sv
    # second to last letter of second word in sv
    # sv1
    # last letter of first word in sv1
    # last letter of second word in sv1
    # second to last letter of first word in sv1
    # second to last letter of seocnd word in sv1
    # svlb
    # second to last letter of first word in svlb
    # second to last letter of second word in svlb
    # sv + sv1
    # last letter of third word in sv or sv1
    # second to last letter of third word in sv or sv1
    return features, string_weight

def split_get(filename):
    """A helper function to return a list of each line of a file with 
    whitepsace removed from each line.

    Arguments:
    filename -- The file to read

    """
    return [line.strip() for line in open(filename).readlines()]

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
        self._table_hash = build_table(self._all_names)
        self._buildFeatures(self._getTrainingData())
        self._tokens = split_get(self._all_names[:self._num_tok])

    def _getTrainingData(self):
        # TODO Too many local variables, perhaps make this several methods?
        # TODO rename _getTrainingData to _get_training_data
        # TODO filter can be replaced by list comprehension
        # TODO We should catch a better Exception
        # TODO Rename the variables: p, q, r, tg, bg
        """Builds and returns the feature sets for the algorithm"""
        #positive_data with contextual information
        featuresets = []
        ptokens = split_get(self.species_train)
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


    def taxon_features(self, token, context_array, index, span):
        # TODO it's long. Perhaps split into several functions?
        # TODO change variable names, at least sv and c and probably others
        # TODO catch a less generic exception
        """Returns a dictionary of features"""
        token = token.strip()
        context_span = self._context_span
        # a now partially populated features dictionary
        features, string_weight = get_basic_features(token)
        
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
            item = strip_token(self._populateFeatures(
                context_array, index + span + c + 1, 0, "end", features,
                str(c + 1) + "_context"))
            #features[str(c+1)+"_context"] = self._populateFeatures(
            #    context_array,index+span+c+1,0,"end",
            #    features,str(c+1)+"_context").strip()
            features[str(c + 1) + "_context"] = item
            if(index + c - context_span < 0):
                features[str(c - context_span) + "_context"] = 'Null'
            else:
                item1 = strip_token(self._populateFeatures(
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

