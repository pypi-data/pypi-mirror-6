#!/usr/bin/env python
# coding: utf-8
"""
Table of Japanese mora to note values for the NSX-1 chip,
as well as helpful functions to deal with the table.
"""

characters = [u'あ', u'い', u'う', u'え', u'お', u'か', u'き', u'く', u'け', u'こ', u'が', u'ぎ', u'ぐ', u'げ', u'ご', u'きゃ', u'きゅ', u'きょ', u'ぎゃ', u'ぎゅ', u'ぎょ', u'さ', u'すぃ', u'す', u'せ', u'そ', u'ざ', u'ずぃ', u'ず', u'ぜ', u'ぞ', u'しゃ', u'し', u'しゅ', u'しぇ', u'しょ', u'じゃ', u'じ', u'じゅ', u'じぇ', u'じょ', u'た', u'てぃ', u'とぅ', u'て', u'と', u'だ', u'でぃ', u'どぅ', u'で', u'ど', u'てゅ', u'でゅ', u'ちゃ', u'ち', u'ちゅ', u'ちぇ', u'ちょ', u'つぁ', u'つぃ', u'つ', u'つぇ', u'つぉ', u'な', u'に', u'ぬ', u'ね', u'の', u'にゃ', u'にゅ', u'にょ', u'は', u'ひ', u'ふ', u'へ', u'ほ', u'ば', u'び', u'ぶ', u'べ', u'ぼ', u'ぱ', u'ぴ', u'ぷ', u'ぺ', u'ぽ', u'ひゃ', u'ひゅ', u'ひょ', u'びゃ', u'びゅ', u'びょ', u'ぴゃ', u'ぴゅ', u'ぴょ', u'ふぁ', u'ふぃ', u'ふゅ', u'ふぇ', u'ふぉ', u'ま', u'み', u'む', u'め', u'も', u'みゃ', u'みゅ', u'みょ', u'や', u'ゆ', u'よ', u'ら', u'り', u'る', u'れ', u'ろ', u'りゃ', u'りゅ', u'りょ', u'わ', u'うぃ', u'うぇ', u'うぉ', u'N\\', u'm', u'N', u'J', u'n']

aliases = {
    u'づぁ': u'ざ',
    u'づぃ': u'ずぃ',
    u'づ': u'ず',
    u'づぇ': u'ぜ',
    u'づぉ': u'ぞ',
    u'ゐ': u'うぃ',
    u'ゑ': u'うぇ',
    u'を': u'うぉ',
    u'ん': u'n', # XXX
}

def characterToNote(c):
    """Convert a single note to its NSX-1 value."""
    if c in aliases:
        c = aliases[c]
    if c in characters:
        return characters.index(c)
    raise ValueError("Invalid note character: %s" % c)

def characterIsValid(c):
    """Determine if a character string represents a valid note mora."""
    if c in aliases:
        c = aliases[c]
    return c in characters

def stringToNotes(s):
    """Convert a string of notes to a list of NSX-1 values."""
    i = 0
    output = []
    while i < len(s):
        candidate = s[i:i+2]
        if characterIsValid(candidate):
            output.append(characterToNote(candidate))
            i += 2
        else:
            candidate = s[i]
            if characterIsValid(candidate):
                output.append(characterToNote(candidate))
            i += 1
    return output


if __name__ == "__main__":
    # Tests
    assert characters[0x00] == u'あ'
    assert characters[0x43] == u'の'
    assert characters[0x68] == u'も'
    assert characters[0x7F] == u'n'

    assert characterToMidi(u'ば') == 0x4C
    assert characterToMidi(u'り') == 0x70

    assert stringToNotes(u"でぃおすみおえすらちゅぱかぶら") == \
            [0x2F, 0x04, 0x17, 0x65, 0x04, 0x03, 0x17, 0x6F, 0x37, 0x51, 0x05, 0x4E, 0x6F]
