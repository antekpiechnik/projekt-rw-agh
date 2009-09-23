#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import string
import time

# dictionarie
origin_bits = ['gr.', 'łc.', 'fr.', 'niem.', 'ang.']

# read the test file
file = open("../test_data/pwn_utf.txt", "r")
data = file.read()
data = data.split('##')

# stats
unprocessed = []
start_time = time.time()

# container for all the definitions found
definitions = []

# the main class for containing the definitions along with the examples/origin and so on
class WordDefinition:

    # the simplest of all constructors
    def __init__(self, name, definition):
        self.name = name
        self.definition = definition
        self.examples = []
        self.origin = ''
        self.additional_defs = []
    
    # method for printing, will be merged with a xml-generating output later on
    def pretty_print(self):
        print "\n**"
        print "Name: %s\nDefinition: %s" % (self.name, self.definition)
        if self.examples:
            print "Examples:"
            for example in self.examples:
                print "- " + example
        if self.origin:
            print "Origin: %s" % self.origin

        if self.additional_defs:
            print "Aditional definitions:\n"
            for a_def in self.additional_defs:
                a_def.pretty_print_tabbed()
    
    # a method for printing the additional definitions (tabbed)
    def pretty_print_tabbed(self):
        print "\n\t*"
        print "\tName: %s\n\tDefinition: %s" % (self.name, self.definition)
        if self.examples:
            print "\tExamples:"
            for example in self.examples:
                print "\t- " + example
        if self.origin:
            print "\tOrigin: %s" % self.origin

                
# function extracting the name of the word being defined
def extract_name(lines):
    word = lines[0].split(' ')[0]
    #print word
    return word


# extracting a definition for the word
def extract_definition(line):
    #print line
    #if line.startswith("<domy"):
    #    print '>> %s' % line
    word_re = re.compile('\w{2,}', re.U)
    line = line.lstrip()
    if not re.search('^[A-Z]', line):
        if '<' in line and '>' in line:
            start_def = string.find(line, "<")
            extras = re.search('[a-z].+[a-z]\.', line[:start_def])
            end_def = string.find(line, ">")
            definition = line[start_def+1:end_def]
            if extras:
                definition = "(%s) %s" % (str(extras.group()), definition)
            return definition
        elif 'czas.' in line or 'rzecz.' in line or 'przym.' in line or 'przysłów.' in line:
            return line
        elif re.search('forma.{2,}\.', line):
            return line
        elif re.search('zwykle.*lm', line):
            return line
        elif not re.search('^[A-Z]', line) and word_re.search(line):
            if not line.startswith("blm") or not line.startswith("blp") or not line.startswith("lm") or not line.startswith("lp"):
                return line
        elif word_re.search(line):
            if not line.startswith("blm") or not line.startswith("blp") or not line.startswith("lm") or not line.startswith("lp"):
                return line
        elif 'w zn.' in line:
            return line
        else:
            return None
    elif line.startswith("D "):
        return extract_definition(line[2:])
    elif re.search('^I+\.?', line):
        return extract_definition(line[len(re.search('^I+\.?', line).group()):])
    else:
        return None

# example extracting method
def extract_example(line):
    line = line.lstrip()
    is_example = re.search('^[A-Z]([a-z]|.){2,}', line)

    if is_example:
        return line
    else:
        return None

# find an origin for the word, using a given dictionary
def extract_origin(line):
    line = line.lstrip()
    for bit in origin_bits:
        if bit in line:
            return line
    else:
        return None

# recognize and extract additional definitions
def extract_additional_def(line):
    line = line.lstrip()
    extras = re.search('^[a-z].+[a-z]\.', line)
    if extras:
        extras = str(extras.group())
        line = line[len(extras):]
    start_def = string.find(line, "<")
    name = line[:start_def]
    line = line[start_def:]
    definition = extract_definition(line)
    if definition:
        if extras:
            definition = "(%s) %s" % (extras, definition)
        return WordDefinition(name, definition)
    else:
        return None

# main carver
def extract_from_lines(lines, name, definition):
    d = False
    word_def = WordDefinition(name, definition)
    if lines:
        for line in lines:
            if re.search('(D )?^([a-z].+[a-z]\.)?\s?[A-Z]', line) and '<' in line and '>' in line:
                if line.startswith("D "):
                    line = line[2:]
                    d = True
                a = extract_additional_def(line)
                if a:
                    word_def.additional_defs.append(a)

            elif re.search('^[A-Z]', line):
                a = extract_example(line)
                if a:
                    word_def.examples.append(a)
    return word_def


for entry in data:
    processed = False
    word_def = None

    entry = entry.split('\n')
    #print entry

    new_entry = []
    for line in entry:
        #print re.sub("\s*", "", line)
        if re.search('\w+', line):
            new_entry.append(line)

    #print new_entry
    entry = new_entry

    numbering_indexes = []

    for line in entry:
        if re.search('^[1-9]\.', line) or re.search('^[a-j]\)', line):
            numbering_indexes.append(entry.index(line))

    name = extract_name(entry)

    #print '>> %s' % name
    
    if not numbering_indexes:
        definition = extract_definition(entry[0][len(name)+1:].lstrip())
        if definition:
            if len(entry) > 1:
                if extract_definition(entry[1]):
                    definition = extract_definition(entry[1])
            word_def = extract_from_lines(entry[1:], name, definition)
        else:
            if len(entry) > 1:
                definition = extract_definition(entry[1])
                if definition:
                    word_def = extract_from_lines(entry[2:], name, definition)
                else:
                    word_def = extract_additional_def(entry[1])
        
        if word_def:
            a = extract_origin(entry[len(entry)-1])
            if a:
                word_def.origin = a
            processed = True
            definitions.append(word_def)

    else:
        new_defs = []
        for ind in numbering_indexes:
            definition = extract_definition(entry[ind][1:])
            if not definition:
                if len(entry) >= ind+2:
                    definition = extract_definition(entry[ind+1])
            else:
                if len(entry) >= ind+2:
                    if extract_definition(entry[ind+1]) and not ind+1 in numbering_indexes:
                        definition = extract_definition(entry[ind+1])

            if definition:
                if numbering_indexes.index(ind) == (len(numbering_indexes)-1):
                    new_defs.append(extract_from_lines(entry[ind+1:], name, definition))
                else:
                    new_defs.append(extract_from_lines(entry[ind+1:numbering_indexes[numbering_indexes.index(ind)+1]], name, definition))
            else:
                a = extract_additional_def(entry[ind][3:])
                if a:
                    new_defs.append(a)
        if new_defs:
            a = extract_origin(entry[len(entry)-1])
            for a_def in new_defs:
                if a:
                    a_def.origin = a
                processed = True
                definitions.append(a_def)

    if not processed:
        unprocessed.append(name)

duration = time.time() - start_time

#for definition in definitions:
    #definition.pretty_print()

print '\n------'
print 'Entries processed: %d' % len(data)
print 'Definitions created: %d' % len(definitions)
if unprocessed:
    print 'Unprocessed: %d (%d%%)' % (len(unprocessed), int(len(unprocessed)*100/(len(data)*1.00)))
    for element in unprocessed:
        print '- %s' % element
print 'Time: %dmin %ds' % (duration/60, duration%60)
print '------\n'

i = 0
for definition in definitions:
    i += 1
    if not i % 6881:
        definition.pretty_print()
    if definition.name == 'przypuszczenie' or definition.name == 'aberracja':
        definition.pretty_print()


