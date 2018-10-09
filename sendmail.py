# George Whitfield 
# gwhitfie@andrew.cmu.edu
# October 8, 2018

import math
import smtplib 
import string
import email
import bz2
import datetime
import random
import copy
import time
from email.message import EmailMessage

############################################################
#
# This file uses the information stored in contacts.txt,
# CurrentN3Words.txt, CurrentN4Words.txt,
# JapSentences.txt and data.txt to send everyone in the Contacts a 
# daily automated email wth Japanese Vocabulary
#
############################################################

# from the 112 website
def bz2readFile(path):
    with bz2.open(path, 'rt') as f:
        return f.read()

def readFile(path):
    with open(path, 'rt') as f:
        return f.read()

# from the 112 website
def writeFile(path, contents):
    with open(path, 'wt') as f:
        f.write(contents)
        
# define all of the necessary file paths
myEmail = 'dailyjapanesevocabulary@gmail.com'
mailNumber = 1
contactsFilePath = 'contacts.txt'
sentencesFilePath = 'sentences.tar.bz2'
japExampleSentences = 'JapSentences.txt' 
numWordsFromEachListToSend = 3
N3VocabularyPath = 'CurrentN3Words.txt'
N4VocuabularyPath =  'CurrentN4Words.txt'
vocabLists = [
    N3VocabularyPath,
    N4VocuabularyPath
]
now = datetime.datetime.now()
dataFilePath = 'data.txt'
data = readFile(dataFilePath )
sendCount = 0

# -------- this function takes about 5 minutes to run---------
# call this function when you need to generate the JapSentences.txt file again
'''
def writeTheJapSentencesToJapExampleSentences(): # THE JAP SENENCES HAVE ALREADY BEEN 
    # GENERATED
    sentences = bz2readFile(sentencesFilePath)
    japSentences = ''
    i = 0
    for line in sentences.splitlines():
        i += 1
        print(i)
        if 'jpn' in line:
            japSentences = japSentences + line + '\n'
    writeFile(japExampleSentences, japSentences)
'''

# ------------- file parsing functions -------------
def parseContacts(filePath):
    contacts = readFile(filePath)
    names = []
    addresses = []
    for info in contacts.splitlines():
        
        details = info.split()
        print(details)
        name = details[0]
        address = details[1]
        names.append(name)
        addresses.append(address)
    return names, addresses
    
def generateNewVocab(filePath):
    # This is what we will return from the function
    newVocabWord = ''
    newVocabReading = ''
    newVocabTranslation = ''
    # helpful variables
    japExampleSentences = ''
    deck = readFile(filePath)
    # file into a list of words
    listOfWords = []
    for line in deck.splitlines():
        listOfWords.append(line)
    wordIndex = random.randint(0,len(listOfWords) - 1)
        # the word, reading, and translation are split in the file with a tab character
    print(deck.splitlines()[wordIndex])
    newVocabWord, newVocabReading, newVocabTranslation = deck.splitlines()[wordIndex].split('\t')
    if newVocabWord == '':
        newVocabWord = newVocabReading
    # overrite the list of words to the file of vocab
    listOfWords.pop(wordIndex)
    for line in listOfWords:
        japExampleSentences = japExampleSentences + str(line) + '\n'
    writeFile(filePath, japExampleSentences)
    return newVocabWord, newVocabReading, newVocabTranslation

def dataParse(data):
    numberOfHoursBetweenEmails = 0
    currentEmailNumber = 0
    for line in data.splitlines():
        if line.startswith('NumberOfHoursBetweenEmails:'):
            numberOfHoursBetweenEmails = line.split()[1]
        elif line.startswith('CurrentEmailNumber:'):
            currentEmailNumber = line.split()[1]
    return  (
        numberOfHoursBetweenEmails,
        currentEmailNumber
    )

def getExampleSentence(vocabWord):
    file = readFile(japExampleSentences)
    file = file.splitlines()
    for sentence in file: # this is A LOT of sentences
        if vocabWord in sentence: # we can improve this line by also checking if
            sentence = sentence.split()[2] # just get the sentence part 
            # there are conjugations of the word in the sentence
            return sentence
    return "Example sentence not found :'("

def updateTheEmailCount(dataFilePath):
    global sendCount
    oldData = copy.deepcopy(readFile(dataFilePath))
    newData = ''
    for line in oldData.splitlines():
        if line.startswith('CurrentEmailNumber:'): # find the line with the current email number
            line = line.split()[0] + ' ' + str(int(line.split()[1]) + sendCount)
        newData = newData + line + '\n'
    writeFile(dataFilePath, newData)


# ------------ email behavior functions --------------------
def createEmailData(vocabLists):
    wordsData = []
    for i in range(numWordsFromEachListToSend):
        for vocabFilePath in vocabLists:
            vocabList = readFile(vocabFilePath)
            newVocabWord, newVocabReading, newVocabTranslation = generateNewVocab(vocabFilePath)
            wordsData.append([
                newVocabWord,
                newVocabReading,
                newVocabTranslation
            ])
    return wordsData

def generateEmailMainBody(listOfDailyWords):
    
    text = ('')
    print(listOfDailyWords)
    for word in range(1, len(listOfDailyWords) + 1):
        vocabWord, reading, translation = listOfDailyWords[word - 1]
        text = text + (
            f'''{word}) {vocabWord} ({reading})  -->  \
{translation}

    Example:
        {getExampleSentence(vocabWord)}

'''
        )
        print(text)
    return text

def sendEmails(vocabLists):
    global sendCount
    names, addresses = parseContacts(contactsFilePath)
    hoursBetweenEmails, currEmail = dataParse(data)
    day = str(int(currEmail) + sendCount)
    # initialize the word of the day list
    wordsOfTheDay = []
    for i in range(numWordsFromEachListToSend):
        for vocList in vocabLists: # the n3 words are fist, then the n4 ones
            newVocabWord, newVocabReading, newVocabTranslation = generateNewVocab(vocList)
            wordsOfTheDay.append((
                newVocabWord,
                newVocabReading,
                newVocabTranslation
            ))
    body = generateEmailMainBody(wordsOfTheDay)
    # setup the server stuff
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # login into the server
    server.login('dailyjapanesevocabulary', 'goes799eat645')
    
    # copied in part from the python documentation
   
    for contact in range(len(addresses)):
        msg = EmailMessage()
        msg['Subject'] = 'Daily Japanese Vocabulary: Day ' + day
        msg['To'] = addresses[contact]
        # make the email message
        msg.set_content('''\
Hi {name},

This is day {day} of your daily Japanese JLPT Vocabulary!
{now.year}/{now.month}/{now.day}

{body}

Feel free to respond to this email if you would like to discontinue the Daily Japanese Vocab service.

Best,

George
Daily Japanese Vocabulary

**Notes**

--> The example sentences are still a work in progress. Right now, they might be off. I'm working to fix that.
        '''.format(name = names[contact], day = day, now = now, body = body ))
        server.sendmail(myEmail, addresses[contact], msg.as_string())
    server.quit()
# run this function to send the emails
def run():
    sendEmails(vocabLists)

# ------------------- Main --------------------
def sendTheEmailsEveryDay(): # recursive function
    numSecondsInADay = 5
    run()
    time.sleep(numSecondsInADay)
    updateTheEmailCount(dataFilePath)

    global sendCount
    sendCount += 1

    sendTheEmailsEveryDay()

sendTheEmailsEveryDay()