#!/usr/bin/env python
# coding: utf-8

# This script generates a story using the Python Wikipedia library. 
# 
# Here's the story premise: A school has piloted an AI teacher to handle classes. The teacher is programmed to answer student questions using Wikipedia as a knowledge base. The students' frequent questions often throw the lesson off plan.

# The working title is "Curious Tangents".

import numpy as np

import re

import wikipedia

import tracery
from tracery.modifiers import base_english

rules = {
    'intro': '#hello.capitalize#, class! Today we\'ll be #discussing# ',
    'explain': ' the #teacher# #said##adverb#.',
    'explain2': 'The #teacher# #said##adverb#, "',
    'continue': 'The #teacher# #ignored# the interruption and #continued#.',
    'continue2': 'The #teacher# #continued#.',
    'acknowledge': 'The #teacher# acknowledged the #question# with a #teacheraction#.',
    'expectquestion': 'The #teacher# #paused#, #expecting# a #question# from the #students# about ',
    'class': 'The #students# #studentaction#.',
    'ask': ' a #student# #asked##adverb#.',
    'return': '"#interjection#, #returning#',
    'bell': 'The bell #rang#.\n\n"That\'s all the time we have. I hope you learned something today," the #teacher# #said##adverb#.\n\nThe #students# #leaveaction# the room#adverb#.',
    'interjection': ['Now', 'Okay', 'Well then', 'Alright', 'So', 'Now then'],
    'hello': ['hello', 'greetings', 'good morning', 'good afternoon', 'welcome', 'hello and welcome'],
    'said': ['said', 'explained', 'declared', 'announced', 'noted', 'breathed', 'seethed', 'elaborated', 'muttered', 'murmured', 'sang'],
    'asked': ['asked', 'queried', 'quizzed','raised', 'questioned', 'demanded', 'wondered', 'said', 'piped up', 'blurted', 'interjected'],
    'continued': ['continued', 'carried on', 'proceeded'],
    'paused': ['paused', 'looked around', 'halted', 'took a breath', 'stopped'],
    'expecting': ['expecting', 'waiting for', 'anticipating', 'listening for'],
    'question': ['question', 'query'],
    'ignored': ['ignored', 'disregarded', 'paid no attention to', 'paid no heed to'],
    'returning': ['returning to ', 'getting back to ', 'turning back our attention to ', 'going back to ', 'back again to '],
    'discussing': ['discussing', 'talking about', 'learning about', 'studying', 'covering'],
    'rang': ['rang', 'sounded', 'blared'],
    'student': ['student', 'pupil', 'boy', 'girl'],
    'students': ['class', 'students', 'pupils'],
    'teacheraction': ['nod', 'smile', 'grin', 'smirk', 'clap of his hands', 'slight jig', 'nervous laugh'],
    'studentaction': ['listened in rapt attention', 
                      'sat straighter in their seats',
                      'watched quietly',
                      'stifled their yawns',
                      'sniggered',
                      'suppressed giggles'],
    'leaveaction': ['shuffled out of',
                    'crowded out of',
                    'left',
                    'vacated',
                    'exited',
                    'filed out of'],
    'teacher': ['teacher', 'instructor', 'professor', 'lecturer', 'educator', 'schoolteacher'],
    'adverb': ['',
               ' confidently', 
               ' pointedly',
               ' aggressively',
               ' timidly',
               ' excitedly',
               ' quietly',
               ' sullenly',
               ' furiously',
               ' happily',
               ' breathlessly',
               ' mechanically',
               ' robotically',
               ' crudely',
               ' politely',
               ' carefully',
               ' calmly',
               ' sadly',
               ' slowly',
               ' gently',
               ' gingerly',
               ' quickly',
               ' patiently']
}

grammar = tracery.Grammar(rules)
grammar.add_modifiers(base_english)

def clean_text(rgx_list, text, replacement=''):
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, replacement, new_text)
    return new_text

def clean_wiki_text(text):
    text = clean_text(['=== .* ===', 
                       '== .* ==', 
                       '\n'], 
                      text, 
                      ' ')
    text = text.replace('"', '\'')
    text = ' '.join(text.split())
    return text

def sorted_links(page):
    c = page.content
    links = [link for link in page.links if link!=page.title]
    locs = {}
    for l in [link for link in page.links if link!=page.title]:
        loc = c.find(l)
        if loc == -1:
            links.remove(l)
        else:
            locs[l]=loc
    return list({k: v for k, v in sorted(locs.items(), key=lambda item: item[1])}.keys())

def lecture_loop(page, limit=5000, threshold=0.30, nest_ratio=0.8):
    """The main lecture loop function
    page: The Wikipedia page being discussed
    limit: The character limit
    threshold: A threshold determining whether or not to do random events
    nest_ratio: A ratio to decrease the character limit for nested lecture loops
    """
    start = 0
    output = ''
    links = sorted_links(page)

    # Is this a continuation of lecture loop?
    continuation=False

    c = clean_wiki_text(page.content)   
    for l in links:
        if np.random.rand()>threshold:
            loc = c.find(l)+len(l)
            if len(output)>limit:
                break
            elif loc>start and loc>0:

                # Parse to sentence later
                output += '\n\n'+grammar.flatten("#explain2#")
                if continuation:
                    output += '-'
                output += c[start:loc]+' -"'
                start = loc - len(l)
                
                if np.random.rand()>threshold:
                    temp = '\n\n"What\'s '+l+'?"'+grammar.flatten("#ask#")
                    output += temp
                    if np.random.rand()>threshold:
                        try:
                            output += '\n\n'+grammar.flatten('#acknowledge#')
                            output += lecture_loop(wikipedia.page(l), limit=int(limit*nest_ratio))
                            output += '\n\n'+grammar.flatten('#return#')+page.title+'....",'+grammar.flatten("#explain#")
                            output += '\n\n'+grammar.flatten('#class#')
                        except:
                            output += '\n\n'+grammar.flatten('#continue#')
                    else:
                        output += '\n\n'+grammar.flatten('#continue#')
                
                else:
                    output += '\n\n'+grammar.flatten('#expectquestion#')+l+' or some other topic.'
                    if np.random.rand()>threshold:
                        output += '\n\n'+grammar.flatten('#class#')
                    output += '\n\n'+grammar.flatten('#continue2#')

                continuation = True

    return output


out = '# Prologue\nThe following is a transcript from the pilot test of the Educator-9000, the world\'s most advanced robotic teacher. No children were harmed in the process. We promise.'
out += '\n\n---'
i = 1
while len(out.split())<51000:
    try:
        topic = wikipedia.page(wikipedia.random())

        print('Writing about', topic.title, '...')
        out += '\n\n# Lesson '+str(i)+': '+topic.title
        out += '\n\n"'+grammar.flatten("#intro#")+topic.title+',"'+grammar.flatten("#explain#")
        out += '\n\n'+grammar.flatten('#class#')
        out += lecture_loop(topic, limit=5000)
        out += '\n\n'+grammar.flatten("#bell#")+'\n\n---'

        i += 1

        text_file = open("NaNoGenMo v3.md", "w", encoding="utf-8")
        text_file.write(out)
        text_file.close()
    except:
        pass
    
out += '\n# Epilogue\n\nThat concludes the testing logs of the Educator-9000. The robotic instructor has met the requirements set out by the board. Immediate deployment is advised.'

text_file = open("NaNoGenMo.md", "w", encoding="utf-8")
text_file.write(out)
text_file.close()