import codecs
import random

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
    lines = split_get(filename)
    # we have to shuffle it, the interwebz said so
    random.shuffle(lines)
    for line in lines:
        # get each individual word from each line
        for name in line.split(" "):
            # to build a set of unique words from a file
            names.add(name.lower())
    return names

def get_basic_features(sentence):
    ## getting a key error, not everything is a trigram....
    """This function takes a three letter sentence and breaks it up into 3
    words and then builds a dictionary of features of the word.

    Arguments:
    stenence -- A trigram or bigram, usually e.g. Gorilla gorilla gorilla

    """
    features = {}
    features["token"] = sentence
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
        features["%s" % word] = name
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
    features["word_3_second_to_last_char_in_sv_or_sv1"] = features["word_3_second_to_last_char"] in letter_lists['sv'] + letter_lists['sv1']

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

    if(string_weight > 18):
        features["string_weight"] = 'A'
    elif(string_weight > 14):
        features["string_weight"] = 'B'
    elif(string_weight > 9):
        features["string_weight"] = 'C'
    elif(string_weight > 4):
        features["string_weight"] = 'D'
    else:
        features["string_weight"] = 'F'

    for vowel in letter_lists['vowels']:
        features["count_of_(%s)" % vowel] = sentence.lower().count(vowel)
        features["has_(%s)" % vowel] = vowel in sentence

    if (len(sentence) > 3):
        features["1up_2_dot_restok"] = (sentence[0].isupper() and
                                        sentence[1] is "." and
                                        sentence[2] is " " and
                                        sentence[3:].islower())
    else:
        features["1up_2_dot_restok"] = False

    features["imp_feature"] = sentence[0].isupper() and sentence[1:].islower()
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
    return [line.strip() for line in codecs.open(filename, 'r', 'utf-8').readlines()]

def remove_dot(string):
    """Return the string with no dot at the end of it.

    Actually, we are only assuming the abbr is 2 or more leters.
    Perhaps it should be >=?

    removes period from words that are not an obvious genus abbreviaion
    sometimes people abbreviate genus to 2 or 3 letters, would it be a problem?
    we assume here that abbr is almost alwqys 1 letter

    Arguments:
    a -- token, usually the first element of a trigram

    """
    if(len(string) > 2 and string[-1] == '.'):
        return string[:-1]
    else:
        return string

def create_index(word_array):
    """Returns a dictionary index of every word in the array. The key is the
    order in which the word appears in the document, the value is the 
    position of the starting character in the document.

    Arguments:
    token -- list of all tokens from the document checked for scientific names

    """
    length = 0
    index = {}
    for i, word in enumerate(word_array):
        index[i] = length
        length = length + len(word) + 1
    return index

def get_offsets(word_array, index, first, second, third):
    """Returns a tuple with start and end positions of a found scientific name.

    Arguments:
    index -- a dictionary containing number of tokens as keys, and corresponding starting position
    of a token in the document agaist whih neti-neti runs as a value
    token_index -- index of the first token from the found scientific name.
    first -- first element of a trigram
    second -- second element of a trigram
    third -- third element of a trigram
    """
    name = first.strip() + " " + second.strip() + " " + third.strip()
    return word_array[token_index], word_array[token_index] + len(name)

def check_end(word):
    """Check the ending of the token. It returns True if token has an ending
    characteristic for a word from a canonical scientific name

    Arguments:
    tok -- the token to check
    """
    ends = ['aceae', 'ales', 'eae', 'idae', 'ina', 'inae', 'ineae',
                'ini', 'mycetes', 'mycota', 'mycotina', 'oidea', 'oideae',
                'opsida', 'phyceae', 'phycidae', 'phyta', 'phytin']
    for value in (remove_dot(word.lower()).endswith(end) for end in ends):
        if value:
            return True
    return False

#def clean_token
