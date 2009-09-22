#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import string

file = open("test1.txt", "r")
data = file.read()
data = data.split('##')

definitions = []

class WordDefinition:
    def __init__(self, name, definition):
        self.name = name
        self.definition = definition
        self.examples = []
        self.origin = ''
        self.additional_defs = []

    def pretty_print(self):
        print "**"
        print "Name: %s\nDefinition: %s" % (self.name, self.definition)
        if self.examples:
            print "Examples:"
            for example in self.examples:
                print "- " + example
        if self.origin:
            print "Origin: %s" % self.origin

        if self.additional_defs:
            print "Aditional definitions:"
            for a_def in self.additional_defs:
                a_def.pretty_print_tabbed()

    def pretty_print_tabbed(self):
        print "\t*"
        print "\tName: %s\n\tDefinition: %s" % (self.name, self.definition)
        if self.examples:
            print "\tExamples:"
            for example in self.examples:
                print "\t- " + example
        if self.origin:
            print "\tOrigin: %s" % self.origin

                

        
def extract_name(lines):
    word = lines[0].split(' ')[0]
    #print word
    return word

def extract_definition(line):
    if not re.search('^[A-Z]', line):
        if '<' in line and '>' in line:
            start_def = string.find(line, "<")
            extras = re.search('[a-z].+[a-z]\.', line[:start_def])
            end_def = string.find(line, ">")
            definition = line[start_def+1:end_def]
            if extras:
                definition = "(%s) %s" % (str(extras.group()), definition)
            return definition
        elif 'czas.' in line or 'rzecz.' in line or 'przym.' in line:
            return line
        elif re.search('forma.{2,}\.', line):
            return line
        elif re.search('zwykle.*lm', line):
            return line
        else:
            return None
    else:
        return None

def extract_example(line):
    is_example = re.search('\s^[A-Z]([a-z]|.){2,}', line)

    if is_example:
        return line
    else:
        return None

def extract_origin(line):
    if 'łc.' in line or 'gr.' in line:
        return line
    else:
        return None

def extract_additional_def(line):
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

def extract_from_lines(lines, name, definition):
    word_def = WordDefinition(name, definition)
    if lines:
        for line in lines:
            if line.startswith("D "):
                line = line[2:]
            
            if re.search('^[A-Z]', line) and '<' in line and '>' in line:
                a = extract_additional_def(line)
                if a:
                    word_def.additional_defs.append(a)

            elif re.search('^[A-Z]', line):
                a = extract_example(line)
                if a:
                    word_def.examples.append(a)
    return word_def
    
for entry in data:
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
        if re.search('^[1-9]\.', line):
            numbering_indexes.append(entry.index(line))

    print numbering_indexes

    name = extract_name(entry)
    
    if not numbering_indexes:
        definition = extract_definition(entry[0][len(name)+1:])
        if definition:
            word_def = extract_from_lines(entry[1:], name, definition)
        else:
            definition = extract_definition(entry[1])
            if definition:
                word_def = extract_from_lines(entry[2:], name, definition)
        
        if word_def:
            a = extract_origin(entry[len(entry)-1])
            if a:
                word_def.origin = a
            print "NORMAL %s" % word_def.name
            definitions.append(word_def)

    else:
        new_defs = []
        for ind in numbering_indexes:
            print ind
            definition = extract_definition(entry[ind][3:])
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
                print "MULTI %s" % a_def.name
                definitions.append(a_def)

                

for definition in definitions:
    definition.pretty_print()

            
        

   # numbered = re.findall("[1-9]\.", entry_text)

    #if not numbered:
    #    cont = process_part(entry_text, word)
    #    cont.pretty_print()
    #else:
    #    numbering_indexes = []
    #    for numbering in numbered:
    #        
    #        print "**** %s ***" % bullet
    #        ay = ay[string.find(ay, bullet)+2:]
    #        cont = process_bit(ay, word)
    #        cont.pretty_print()
    #        
    #print ay

