
def left_strip(t):
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
def right_strip(t):
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

def get_slice(array, slice):
    try:
        return eval("array%s" % slice)
    except IndexError:
        return "Null"

