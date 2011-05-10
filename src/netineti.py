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

    def __init__(self, model_object, black_list_file='data/new-list.txt'):
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

    def find_names(self, text, resolve_dot=False):
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
        # TODO: see if a saner split will still work
        prog = re.compile('\s')
        tokens = prog.split(text)
        #tokens = [line for token in tokens for line in token.split("\\\\\\\\n")]

        names, newnames, offsets = self.findNames(tokens)
        name_set = set(names)
        name_list = list(name_set)
        resolved_names = []
        name_dict = {}
        prog = re.compile('^(.{1})([^ ]+)(.*)$')
        if(resolve_dot):
            abbr_names = [a for a in name_list if(a[1] == "." and a[2] == " ")]
            diff = name_set.difference(set(abbr_names))
            diff_list = list(diff)
            for name in diff_list:
                result = prog.match(name).groups()
                name_dict[result[0] + "." + result[2]] = result[1]
            for name in abbr_names:
                if(name_dict.has_key(name)):
                    resolved_names.append(name[0] + "[" + name_dict[name] + "]" + " " + name[3:])
                else:
                    resolved_names.append(name)
            resolved_names += diff_list
            resolved_names.sort()
        else:
            name_list.sort()
            resolved_names = name_list
        return "\n".join(resolved_names), newnames, offsets

    def _hCheck(self, a):
        # TODO change name to something useful, not _h_check
        # TODO change variables (a, w, j, e1) to something useful
        """Returns a boolean.
        checks if a word is in a black list

        Arguments:
        a -- a token, first element of a trigram

        """
        a = remove_dot(a)
        e1 = a.split("-")
        j = [self._black_dict.has_key(w) for w in e1]
        return(not True in j and not self._black_dict.has_key(a.lower()))

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
                a.isalpha()) or td) and (remove_dot(b).isalpha() or '-' in b)
            return(s1 and self._hCheck(a) and self._hCheck(b))
        else:
            return False

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
            s1 = c.islower() and remove_dot(c).isalpha()
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
        return((self._model_object.get_model().classify(
            self._model_object.taxon_features(tkn, context, index, span)) ==
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
        #gr =remove_dot((a+" "+b+" "+c).strip())
        if(b == ""):
            gr = remove_dot((a + " " + c).strip())
        else:
            gr = remove_dot((a + " " + b + " " + c).strip())
        if(gr[1] == "." and gr[2] == " "):
            if(nhash.has_key(gr)):
                nms.append(remove_dot((a[0] + "[" + nhash[gr] + "]" + " " +
                                        b + " " + c).strip()))
            elif(last_genus and a[0] == last_genus[0]):
                nms.append(remove_dot((a[0] + "[" + last_genus[1:] + "]" +
                                        " " + b + " " + c).strip()))
            elif(plg and a[0] == plg):
                nms.append(remove_dot((a[0] + "[" + plg[1:] + "]" + " " +
                                        b + " " + c).strip()))
            else:
                nms.append(gr)
        else:
            nms.append(gr)
            nhash[remove_dot((a[0] + ". " + b + " " + c).strip())] = a[1:]


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
            (remove_dot(tok).isalpha() or (tok[0].isupper() and
                                        tok[1] == "." and tok[2].islower() and
                                        remove_dot(tok[2:]).isalpha())) and
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
        if(len(filter(lambda x: remove_dot(tok.lower()).endswith(x),
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
        oh = create_index(token)
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
                p, q, r = clean_token(a.strip(), b.strip(), c)
                #p1,q1,r1 = a.strip(),b.strip(),c.strip()
                #print "p q r = ", p,"--",q,"--",r
                #print "p1,q1,r1 = ",p1,q1,r1
                bg = remove_dot(p + " " + q)
                tg = remove_dot(p + " " + q + " " + r)
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
                    if(self._taxonTest(re.sub("\.", ". ", remove_dot(p)),
                                        token, icount, 0)):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(remove_dot(p))
                    elif(self._endingCheck(p)):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(remove_dot(p))
                elif(self._endingCheck(p)):
                    if(self._hCheck(p) and p[0].isupper() and
                        remove_dot(p).isalpha()):
                        start, end = self._getOffsets(oh, icount, a, "", "")
                        offset_list.append((start, end))
                        nms.append(remove_dot(p))
        try:
            if(self._isGood2(tgr[-1][-2], tgr[-1][-1])):
                if(self._taxonTest(remove_dot(tgr[-1][-2] + " " +
                    tgr[-1][-1]), token, icount + 1, 1)):
                    self._resolve(tgr[-1][-2], tgr[-1][-1], "", nhash, nms,
                    last_genus, prev_last_genus)
                    #nms.append(remove_dot(tgr[-1][-2]+" "+tgr[-1][-1]))
                elif(self._uninomialCheck(tgr[-1][-2])):
                    if(self._taxonTest(re.sub("\.", " ",
                        remove_dot(tgr[-1][-2])), token, icount + 1, 0)):
                        nms.append(remove_dot(tgr[-1][-2]))
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


if __name__ == '__main__':
    print "NETI..NETI\n"
