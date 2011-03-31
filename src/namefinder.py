from utilities import split_get, left_split, right_split, strip_token

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
        e_list -- a list of exceptions (default "data/new-list.txt")

        """
        reml = set()
        elist = split_get(e_list)
        for exception in elist:
            reml.add(exception)
        self._remlist = reml
        self._modelObject = modelObject
        self._clnr = TextClean()

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
        j = [word in self._remlist for word in e1]
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
        # no. fuck no. I have no idea why this is doing this
        # it makes a list that repeats the paragraph (WORD COUNT) TIMES
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
                ra = left_strip(a1)[0]
            else:
                ra = strip_token(a1)
        if(len(b1) > 1):
            if(b1[0] + b1[-1] == "()"):
                pass
            elif(b1[-1] == "-"):
                rb = left_strip(b1)[0]
            else:
                rb = strip_token(b1)
        return(ra, rb, strip_token(c))

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
