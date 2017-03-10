#! /usr/bin/env python
from __future__ import print_function
import sys
from fontTools.ttLib import TTFont
import json

def setNames(font, nameRecords):
    nameTable = font['name']
    for nameRecord in nameRecords:

        nameRecord = list(nameRecord)
        if type(nameRecord[4]) is not int:
                # expecting here a string like "0x409",JSON has no own hex digit notation
                nameRecord[4] = int(nameRecord[4], 16)

        if nameRecord[0] == None:
            # delete
            deleteKey = tuple(nameRecord[1:5])
            names = []
            for name in nameTable.names:
                # so in the deleteKey None can be used as a wildcard
                key = (  name.nameID if deleteKey[0] is not None else None
                       , name.platformID if deleteKey[1] is not None else None
                       , name.platEncID if deleteKey[2] is not None else None
                       , name.langID if deleteKey[3] is not None else None
                )
                if key == deleteKey:
                    continue
                names.append(name)
            nameTable.names = names
        else:
            # a nameRecord must be structured like this:
            # [(string)data, (int)nameID, (int)platformID, (int)platEncID, (int or hex-string)langID]
            nameTable.setName(*nameRecord)

def writeData(font, data):
    for name, item in data.items():
        if name == 'name':
            setNames(font, item)
        # TODO: more special implementations for other tables should go here.
        # ALSO: `name` must not necessarily be the name for the table
        # much rather, it must understand how to use the data in `item`
        # elif name = 'another special case':
        #       setSpecialCaseData(font, item)
        else:
            # generic implementation, `name` == a table name
            # the table must exist already.
            table = font[name]
            for key, value in item:
                setattr(table, key, value)

def clean(font):
    # remove non-standard 'FFTM' the FontForge time stamp table
    if 'FFTM' in font:
        del font['FFTM'];

    # according to fontbakery:
    # ost table should be version 2 instead of 3.0.More info at
    # https://github.com/google/fonts/issues/215
    if font['post'].formatType != 2.0:
        post = font["post"]
        glyphOrder = font.getGlyphOrder()
        post.formatType = 2.0
        post.extraNames = []
        post.mapping = {}
        post.glyphOrder = glyphOrder

    # force compiling tables by fontTools, saves few tens of KBs
    for tag in font.keys():
        if hasattr(font[tag], "compile"):
            font[tag].compile(font)

def main():
    infile = sys.argv[1]
    outfile = sys.argv[2]
    jsonSources = sys.argv[3:]

    font = TTFont(infile)

    i = 0
    while i+1 < len(jsonSources):
        sourcetype = jsonSources[i]
        sourcedata = jsonSources[i+1]
        if sourcetype == '-r':
            # raw, the sourcedata is the json
            data = json.loads(sourcedata)
        elif sourcetype == '-f':
            # file, the sourcedata is a json file name
            with open(sourcedata) as f:
                data = json.load(f)
        else:
            raise ValueError('unknown json source type "{0}"'.format(sourcetype))

        writeData(font, data);
        i += 2

    clean(font)
    font.save(outfile)
    font.close()


if __name__ == '__main__':
    main()
