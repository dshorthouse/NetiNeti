import re

rstrip = re.compile(u'^(.*?)([\W\d_]*)$', re.U | re.M)
lstrip = re.compile(u'^([\W\d_]*)(.*)$', re.U | re.M)



def left_strip(token):
    # TODO rename method
    # TODO rename variables
    """This takes a token and strips non alpha characters off the left. It
    returns the stripped string and the number of characters it stripped.

    Arguments:
    token -- a one word token which might have trailing non alpha characters

    """
    #stripped, not_stripped = lstrip.match(token).groups()
    #return not_stripped, len(stripped)
    i = 0
    while(i < len(token)):
        if(not token[i].isalpha()):
            i = i + 1
        else:
            break
    if(i == len(token)):
        return('', 0)
    return(token[i:], i)

# This strips non alpha characters from the right of a string
# and returns the new string and the number of characters stripped negated
def right_strip(token):
    # TODO rename method
    # TODO rename variables
    """This takes a token and strips non alpha characters off the right. It
    returns the stripped string and the number of characters it stripped.

    amount of stripped characters allows to calculate locations of found
    scientific names within the original document

    Arguments:
    t -- a one word token

    """

    #not_stripped, stripped = rstrip.match(token).groups()
    #return not_stripped, len(stripped)
    j = -1
    while(j >= -len(token)):
        if(not token[j].isalpha()):
            j = j - 1
        else:
            break
    if(j == -1):
        return(token, 0)
    elif(j == -(len(token) + 1)):
        return('', 0)
    else:
        return(token[:j + 1], j + 1)

def striptok(t):
    # TODO rename method
    # TODO rename variables
    """This combines left_strip and right_strip into one method.
    Returns back token without trailing non alpha characters

    Arguments:
    t -- a one word token which might contain trailing non alpha characters
         like parentheses, comma, etc...

    """
    return(right_strip(left_strip(t)[0])[0])

def get_words_slice(words, word_index, first_char_index, second_char_index = None):
    result = 'Null'
    try:
        if (second_char_index == None):
            result = words[word_index][first_char_index]
        else:
            result = words[word_index][first_char_index:second_char_index]
    except IndexError:
        pass
    if result == []: result = 'Null'
    return result

def remove_dot(string):
    """Return the string with no dot at the end of it.

    removes period from words that are not an obvious genus abbreviaion
    sometimes people abbreviate genus to 2 or 3 letters, would it be a problem?
    we assume here that abbr is almost alwqys 1 letter

    Arguments:
    a -- token, usually the first element of a trigram

    """
    if len(string) > 2:
        return string.rstrip(".")
    else:
        return string

def clean_token(a, b, c):
    # TODO rename method to _clean_tokens or similar
    # TODO rename variables (a, b, c, a1, b1, ra, rb)
    """Cleans the tokens.
    Intelligent strip of trigram parts. We are assuming a and b are stripped

    Arguments:
    a -- first element of a trigram
    b -- second element of a trigram
    c -- third element of a trigram

    """
    ra = a
    rb = b
    if len(a) > 1:
        if a[-1] == ".":
            ra = left_strip(a)[0]
        else:
            ra = striptok(a)
    if len(b) > 1:
        if b[0] + b[-1] == "()":
            pass
        elif b[-1] == "-":
            rb = left_strip(b)[0]
        else:
            rb = striptok(b)
    return ra, rb, striptok(c)

def create_index(token):
    # TODO rename method to _create_index or similar
    # TODO there is lots of programming cleanup that can happen here
    # TODO rename variables, specifically oh
    # TODO could remove method from the class
    """Returns a dictionary indexes for all tockens. Key is a token number in
    the document, Value is the length of the token.

    Arguments:
    token -- list of all tokens from the document checked for scientific names

    """
    length = len(token[0]) + 1
    oh = {0:0}
    for i in range(1,len(token)):
        oh[i] = length
        length = length + len(token[i]) + 1 #or delim length
    return oh
