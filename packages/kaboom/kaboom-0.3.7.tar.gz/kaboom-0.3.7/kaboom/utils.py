 # following description appears in levenshtein distance offered by git
 # at https://github.com/git/git/blob/master/levenshtein.c

 # This function implements the Damerau-Levenshtein algorithm to
 # calculate a distance between strings.
 #
 # Basically, it says how many letters need to be swapped, substituted,
 # deleted from, or added to string1, at least, to get string2.
 #
 # The idea is to build a distance matrix for the substrings of both
 # strings.  To avoid a large space complexity, only the last three rows
 # are kept in memory (if swaps had the same or higher cost as one deletion
 # plus one insertion, only two rows would be needed).
 #
 # At any stage, "i + 1" denotes the length of the current substring of
 # string1 that the distance is calculated for.
 #
 # row2 holds the current row, row1 the previous row (i.e. for the substring
 # of string1 of length "i"), and row0 the row before that.
 #
 # In other words, at the start of the big loop, row2[j + 1] contains the
 # Damerau-Levenshtein distance between the substring of string1 of length
 # "i" and the substring of string2 of length "j + 1".
 #
 # All the big loop does is determine the partial minimum-cost paths.
 #
 # It does so by calculating the costs of the path ending in characters
 # i (in string1) and j (in string2), respectively, given that the last
 # operation is a substitution, a swap, a deletion, or an insertion.
 #
 # This implementation allows the costs to be weighted:
 #
 # - w (as in "sWap")
 # - s (as in "Substitution")
 # - a (for insertion, AKA "Add")
 # - d (as in "Deletion")
 #
 #  Note that this algorithm calculates a distance _iff_ d == a.


def levenshtein(string1, string2, swap=0, substitution=2, insertion=1, deletion=3):
    """
    This is levenshtein distance calculation utility taken from
    https://github.com/git/git/blob/master/levenshtein.c

    @param string1:
    @param string2:
    @param swap:
    @param substitution:
    @param insertion:
    @param deletion:
    @return:
    """
    len1 = len(string1)
    len2 = len(string2)

    row0 = list()
    row1 = list()
    row2 = [0] * (len2 + 1)

    for j in range(len2 + 1):
        row1.append(j * insertion)

    for i in range(len1):
        # print i
        dummy = [0] * (len2 + 1)
        row2[0] = (i + 1) * deletion
        for j in range(len2):
            # substitution
            row2[j + 1] = row1[j] + substitution * (string1[i] != string2[j])
            # swap
            if (i > 0 and j > 0 and string1[i-1] == string2[j]
                    and string1[i] == string2[j-1] and
                    row2[j+1] > row0[j-1] + swap):
                row2[j + 1] = row0[j - 1] + swap
            # deletion
            if row2[j + 1] > row1[j + 1] + deletion:
                row2[j + 1] = row1[j + 1] + deletion
            # insertion
            if row2[j + 1] > row2[j] + insertion:
                row2[j + 1] = row2[j] + insertion
        dummy, row0, row1, row2 = row0, row1, row2, dummy

    return row1[len2]


def did_you_mean(string1, strings):
    """
    Takes string1 and calculates levenshtein distance from strings
    and returns most likely string
    @param string1:
    @param strings:
    """
    if not strings:
        return None
    result = strings[0]
    result_distance = levenshtein(string1, strings[0])
    for command in strings[1:]:
        new_distance = levenshtein(string1, command)
        if new_distance < result_distance:
            result, result_distance = command, new_distance

    return result
