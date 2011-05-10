# Machine Learning based approach to find scientific names # Input: Any text preferably in Engish
# Output : A list of scientific names

"""
netineti.py

Created by Lakshmi Manohar Akella.
Updated on October 27 2010 (ver 0.945).
Copyright (c) 2010, Marine Biological Laboratory. All rights resersved.

"""
import time
import os
import nltk
from neti_neti_trainer import NetiNetiTrainer
from neti_neti_helper import *
import re

class NameFinder():
    """The meat of NetiNeti. This class uses the trained NetiNetiTrain model
    and searches through text to find names.

    This version supports offsets.

    """

    def __init__(self, model_object, black_list_file='data/black-list.txt'):
        # TODO change the variables e_list, a and reml to something useful
        """Create the name finder object.

        Arguments:
        model_object -- maybe the trained NetiNetiTrain object?

        Keyword Arguments:
        e_list -- describe argument (default "data/new-list.txt")

        """
        self._black_dict = {}
        f = open(os.path.dirname(os.path.realpath(__file__)) + "/"  +
                     black_list_file)
        for line in f:
            self._black_dict[line.rstrip()] = 1
        self._model_object = model_object
        self._text = ''
        self._names_list = []
        self._offsets_list = []
        self._names_dict = {}
        self._index_dict = {}
        self._last_genus = ''
        self._prev_last_genus = ''
        self._count = -1

    def find_names(self, text, resolve_abbreviated_names = False):
        # TODO fix variable names
        # TODO perhaps break this up into smaller functions
        """
        Return a string of names concatenated with a newline and a list of
        offsets for each mention of the name in the original text.

        Arguments:
        text -- input text

        Keyword Arguments:
        resolvedot -- boolean to add abbreviated version of a genus string (false by default) and not
                      recommended for use
        """
        self._text = text
        space_regex = re.compile('\s')
        tokens = space_regex.split(text) #any reason not to use nltk tokenizer?

        names, names_occurance, offsets = self._find_names_in_tokens(tokens)
        names_set = set(names)
        names_list = list(names_set)
        resolved_names = None
        if resolve_abbreviated_names:
            resolved_names = self._resolve_abbreviated_names(names_list, names_set)
        else:
            names_list.sort()
            resolved_names = names_list
        return "\n".join(resolved_names), names_occurance, offsets

    def _find_names_in_tokens(self, token):
        """
        takes list of all tokens from a document and returns back tuple
        of found names. First element is a an alphabetised list of unique names, second -- names in the order of their occurance in the document, third --  offsets for each mention of the name in the document

        Arguments:
        token -- list with all tokens from the document searched for scientific names

        """
        ts = time.clock()
        self._index_dict = create_index(token)
        token_string = " ".join(token)
        if(len(token) == 2):
            if(self._is_like_binomial(token[0], token[1]) and self._is_a_name(token_string, token, 0, 1)):
                self._names_list.append(token_string)
        elif(len(token) == 1):
            if(len(token[0]) > 2 and token[0][0].isupper() and
                token[0].isalpha() and self._is_not_in_black_list(token[0]) and
                self._is_a_name(token[0], token, 0, 0)):
                self._names_list.append(token[0])
        else:
            tgr = nltk.trigrams(token)
            #not generating bigrams...getting them from trigrams..
            # little more efficient
            for a, b, c in tgr:
                self._count += 1
                #print a,self._count
                p, q, r = clean_token(a.strip(), b.strip(), c)
                #p1,q1,r1 = a.strip(),b.strip(),c.strip()
                #print "p q r = ", p,"--",q,"--",r
                #print "p1,q1,r1 = ",p1,q1,r1
                bg = remove_trailing_period(p + " " + q)
                tg = remove_trailing_period(p + " " + q + " " + r)
                j = -1
                count = 0
                if(self._names_list):
                    while(abs(j) <= len(self._names_list)):
                        if(self._names_list[j][1] != "[" and self._names_list[j][1] != "."):
                            if(count == 0):
                                self._last_genus = self._names_list[j].split(" ")[0]
                                count = count + 1
                            else:
                                self._prev_last_genus = self._names_list[j].split(" ")[0]
                                break
                        j = j - 1
                if(self._is_like_trinomial(p, q, r)):
                    #print "good trigram ...."
                    if(self._is_a_name(tg, token, self._count, 2)):
                        #print "passed trigram..."
                        start, end = self._getOffsets(self._index_dict, self._count, a, b, c)
                        self._offsets_list.append((start, end))
                        self._resolve(p, q, r, self._names_dict, self._names_list, self._last_genus,
                                      self._prev_last_genus)
                elif(self._is_like_binomial(p, q)):
                    #print "good bigram..."
                    if(self._is_a_name(bg, token, self._count, 1)):
                        #print "passed bigram..."
                        start, end = self._getOffsets(self._index_dict, self._count, a, b, "")
                        self._offsets_list.append((start, end))
                        self._resolve(p, q, "", self._names_dict, self._names_list, self._last_genus,
                                      self._prev_last_genus)
                elif(self._is_like_uninomial(p)):
                    if(self._is_a_name(re.sub("\.", ". ", remove_trailing_period(p)),
                                        token, self._count, 0)):
                        start, end = self._getOffsets(self._index_dict, self._count, a, "", "")
                        self._offsets_list.append((start, end))
                        self._names_list.append(remove_trailing_period(p))
                    elif(self._endingCheck(p)):
                        start, end = self._getOffsets(self._index_dict, self._count, a, "", "")
                        self._offsets_list.append((start, end))
                        self._names_list.append(remove_trailing_period(p))
                elif(self._endingCheck(p)):
                    if(self._is_not_in_black_list(p) and p[0].isupper() and
                        remove_trailing_period(p).isalpha()):
                        start, end = self._getOffsets(self._index_dict, self._count, a, "", "")
                        self._offsets_list.append((start, end))
                        self._names_list.append(remove_trailing_period(p))
        try:
            if(self._is_like_binomial(tgr[-1][-2], tgr[-1][-1])):
                if(self._is_a_name(remove_trailing_period(tgr[-1][-2] + " " +
                    tgr[-1][-1]), token, self._count + 1, 1)):
                    self._resolve(tgr[-1][-2], tgr[-1][-1], "", self._names_dict, self._names_list,
                    self._last_genus, self._prev_last_genus)
                    #self._names_list.append(remove_trailing_period(tgr[-1][-2]+" "+tgr[-1][-1]))
                elif(self._is_like_uninomial(tgr[-1][-2])):
                    if(self._is_a_name(re.sub("\.", " ",
                        remove_trailing_period(tgr[-1][-2])), token, self._count + 1, 0)):
                        self._names_list.append(remove_trailing_period(tgr[-1][-2]))
        except Exception:
            print ""
        te = time.clock()
        nnewn = []
        nnofl = []
        #print len(self._offsets_list)
        for o in self._offsets_list:
            nme = self._text[o[0]:o[1]]
            pts = nme.split(" ")
            if(pts[0][0] + pts[0][-1] == "()"):
                #print nme+"...."
                no1 = o[0]
                no2 = o[1] + right_strip(nme)[1]
            else:
                #print nme
                #print "o1 ",o[0]
                #print "o2 ",o[1]
                #print "left strip...", left_strip(nme)[1]
                #print "right strip...",right_strip(nme)[1]
                #print "................."
                no1 = o[0] + left_strip(nme)[1]
                no2 = o[1] + right_strip(nme)[1]
            tj = self._text[no1:no2]
            nnewn.append(tj)
            nnofl.append((no1, no2))
        print (te - ts)
        #print len(nnewn)
        #print len(nnofl)
        return(self._names_list, nnewn, nnofl)

    def _resolve_abbreviated_names(self, names_list, names_set):
        """
        list of names is augmented with versions of names where genus part is abbreviated
        """
        name_regex = re.compile('^(.{1})([^ ]+)(.*)$') # (B)(etula) (verucosa verucosa)
        names_dict = {}
        resolved_names = []
        abbr_names = [name for name in names_list if (name[1] == "." and name[2] == " ")]
        full_names = names_set.difference(set(abbr_names))
        full_names_list = list(full_names)
        for name in full_names_list:
            result = name_regex.match(name).groups()
            names_dict[result[0] + "." + result[2]] = result[1]
        print names_dict.keys()
        for name in abbr_names:
            if names_dict.has_key(name):
                resolved_names.append(name[0] + "[" + names_dict[name] + "]" + " " + name[3:])
            else:
                resolved_names.append(name)
        resolved_names += full_names_list
        resolved_names.sort()
        return resolved_names

    def _is_like_uninomial(self, word):
        """Returns a boolean
        Checks if a word looks like a uninomial.

        Arguments:
        word -- a word to check as a ponential uninomial

        """
        #TODO: This method currently only allows uninomials of size larger than 5,
        # however there are uninomials which are 2 characters in size.

        is_like_uninomial = (len(word) > 5 and word[0].isupper() and word[1:].islower() and
            (remove_trailing_period(word).isalpha() or (word[0].isupper() and
                                        word[1] == "." and word[2].islower() and
                                        remove_trailing_period(word[2:]).isalpha())) and
                                        self._is_not_in_black_list(word))
        return is_like_uninomial

    def _is_like_binomial(self, first_word, second_word):
        """Returns a boolean.
        Checks if first_word bigram can potentially be a binomial name

        Arguments:
        first_word -- first element of a bigram
        second_word -- second element of a bigram

        """
        if len(first_word) > 1 and len(second_word) > 1:
            is_abbr_word = (first_word[1] == '.' and len(first_word) == 2)
            is_a_candidate = first_word[0].isupper() and second_word.islower() and ((first_word[1:].islower() and
                first_word.isalpha()) or is_abbr_word) and (remove_trailing_period(second_word).isalpha() or '-' in second_word)
            return(is_a_candidate and self._is_not_in_black_list(first_word) and self._is_not_in_black_list(second_word))
        else:
            return False

    def _is_like_trinomial(self, first_word, second_word, third_word):
        """Returns a boolean.
        Checks if a trigram looks like a trinomial name

        Arguments:
        first_word -- first element of a trigram
        second_word -- second element of a trigram
        third_word -- third element of a trigram

        """
        if len(first_word) > 1 and len(second_word) > 1 and len(third_word) > 1:
            third_word_ok = third_word.islower() and remove_trailing_period(third_word).isalpha()

            if second_word[0] + second_word[-1] == "()":
                second_word_ok = second_word[1].isupper() and ((second_word[2] == "." and len(second_word) == 4) or
                                        second_word[2:-1].islower() and
                                        second_word[2:-1].isalpha()) and second_word[-1] != "."
                return (second_word_ok and third_word_ok and self._is_not_in_black_list(third_word) and (first_word[0].isupper() and
                                                         ((first_word[1] == "." and
                                                           len(first_word) == 2) or
                                                          first_word[1:].islower() and
                                                          first_word.isalpha())))
            else:
                return (third_word_ok and self._is_like_binomial(first_word, second_word) and self._is_not_in_black_list(third_word))
        elif len(first_word) > 1 and len(second_word) == 0 and len(third_word) > 1:
            return self._is_like_binomial(first_word, third_word)
        else:
            return False

    def _is_not_in_black_list(self, word):
        # TODO change name to something useful, not _h_check
        # TODO change variables (word, w, j, e1) to something useful
        """Returns a boolean.
        checks if a word is in a black list

        Arguments:
        word -- a token, first element of a trigram

        """
        word = remove_trailing_period(word)
        word_parts = word.split("-")
        res = [self._black_dict.has_key(part) for part in word_parts]
        return (True not in res and not self._black_dict.has_key(word.lower()))

    def _is_a_name(self, token, context, index, span):
        """Checks if a token is a scientific name or not.

        Arguments:
        token -- a name string consisting of 1-3 words
        context -- list of words surrounding the token
        index -- index where the token happens in the document
        span -- length of the token in the document
        """
        features = self._model_object.taxon_features(token, context, index, span)
        return self._model_object.get_model().classify(features) == 'taxon'

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
        #gr =remove_trailing_period((a+" "+b+" "+c).strip())
        if(b == ""):
            gr = remove_trailing_period((a + " " + c).strip())
        else:
            gr = remove_trailing_period((a + " " + b + " " + c).strip())
        if(gr[1] == "." and gr[2] == " "):
            if(nhash.has_key(gr)):
                nms.append(remove_trailing_period((a[0] + "[" + nhash[gr] + "]" + " " +
                                        b + " " + c).strip()))
            elif(last_genus and a[0] == last_genus[0]):
                nms.append(remove_trailing_period((a[0] + "[" + last_genus[1:] + "]" +
                                        " " + b + " " + c).strip()))
            elif(plg and a[0] == plg):
                nms.append(remove_trailing_period((a[0] + "[" + plg[1:] + "]" + " " +
                                        b + " " + c).strip()))
            else:
                nms.append(gr)
        else:
            nms.append(gr)
            nhash[remove_trailing_period((a[0] + ". " + b + " " + c).strip())] = a[1:]


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
        if(len(filter(lambda x: remove_trailing_period(tok.lower()).endswith(x),
                                            endings)) > 0):
            return(True)
        else:
            return(False)


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


if __name__ == '__main__':
    print "NETI..NETI\n"
