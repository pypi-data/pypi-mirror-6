#!/usr/bin/env python
# encoding: utf-8

import difflib
s1 = "Und dann war auf einmal alles ein bissschen anders"
s2 = "Und dann war auf einmal alles ein bisschen anders"


def show_diff(old, new):
    """Will return a HTML string showing the differences between the old and
    the new string.

    The new string will have some markup to show the differences between
    the given strings. Words which has been deleted in the new string
    are marked with a *span* tag with the class *formed-deleted-value*.
    Elements which are new in the new string are marked with a span tag
    having the class *formed-new-value*.

    :old: Old string
    :new: New string
    :returns: A HTML string showing the differences.

    """
    out = []
    mode = None
    d = difflib.Differ()
    old = old.split(" ")
    new = new.split(" ")
    #print old, new
    diff = d.compare(old, new)
    for x in diff:
        if x[0:2] == "+ " and mode != "new":
            if mode:
                out.append("</%s>" % mode)
                mode = None
            out.append("<new>")
            mode = "new"
        elif x[0:2] == "- " and mode != "del":
            if mode:
                out.append("</%s>" % mode)
                mode = None
            out.append("<del>")
            mode = "del"
        elif x[0:2] == "  ":
            if mode:
                out.append("</%s>" % mode)
                mode = None
        elif x[0:2] == "? ":
            continue
        out.append("%s " % "".join(x[2::]))
    if mode:
        out.append("</%s>" % mode)
    return "".join(out)

print show_diff(s1, s2)
