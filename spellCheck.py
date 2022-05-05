'''
COMP 1405 - Fall 2020
Assignment #5

Name: Fabrice Mikobi
ID: 101196480
Comments: Thank You TAs for your hard work :)
'''
# Import copy for deep copy of dictionary
import copy

def load(fileName:str):
    '''
    Reads the content of the provided file and returns words individually for spell check. 
    Also returns the original text for correction.

        Pre-condition: fileName must be a correct file location.

        Post-condition: returns (listOfWords,originalText).
    '''
    try:
        f = open(fileName) # Open file
        listofWords = []
        originalText = ''

        for line in f: # Read file
            originalText += line
            wrds = line.split() # Get every word from the file
            for word in wrds:# Go through every letter
                word = word.split('.')[0] # Remove period.
                listofWords.append(word.lower()) # Add to list
        
        f.close() #Close file
        return listofWords, originalText # Return every word in file and the original text for correction purposes.
    except IOError:
        print('The file could not be opened.')

def spell(wordsToCheck, knownWords, prevMistakes = {}):
    '''
    Executes a spell check on the previously loaded file. 
        - Any word that is not in knownWords is suspected to be misspelled and shown to the user.
        - The user then has the option of accepting it as correct (by pressing enter key) OR of correcting it
        by entering the correct word.
        - Suggestions are shown to the user if the misspelled word was corrected in a previous document or in the same program. 
            Suggestions are shown in decreasing order from the most frequent to the least frequent. 
            All possible spelling of the misspelled words are shown in suggestions square brackets.
        - The function updates the data in mymistakes.txt (if present) and increments the number of corrections for a specific word in mymistakes.txt
        - The function records the words accepted as correct in a List to later add them to mywords.txt
    Parameters:
        - wordsToCheck: List of every word in the previously loaded file
        - knownWords: List of words from words.txt and mywords.txt IF present. It represents all known spelling of words.
        - previousMistakes: Dictionary of mistakes recorded from previous files. May be empty if no mistake data was written to mymistakes.txt before.
    
    Post-condition: returns a dictionary with data to write in mywords.txt and mymistake.txt 

    Note:
        - {mistakes} is the dictionary that stores information about misspelled words. It has the FORM: 
        {'mistake1': [('correct1', #correct, [loc1,loc2]), ('correct2', #correct, [loc3])], 'mistakeN': [('correct1', #correct,[loc1,locN,...])]}.
            Where each KEY is a misspelled word. Its value is a list. In the list is a tuple of 3 elements: 
            [0:str] is the correct spelling. [1:int] is the number of times the misspelled word was corrected to [0]. 
            [2: list] is a list that holds which occurrence of mistakeN was corrected to 'correctN'.
        - {returnedValue} is the dictionary that is returned. 
    '''
    suggestion = '[no suggestions]'
    knownCorrection = set() # create set to avoid redundancies.
    mistakes = copy.deepcopy(prevMistakes) # make a deep copy of the known mistake from mymistakes.txt.
   
    for word in mistakes:
        for k in range(len(mistakes[word])):
            mistakes[word][k] = (mistakes[word][k][0], 0)  # Set the occurrence of mistakes to 0 for every word when the program start


    returnedValue = {'myWords': [], 'mistakes': mistakes} # the dictionary to return
    numCorrections = {} # records the number of correction for every user input.
    mistakeOccurrence = {} # records which occurrence of misspelled word was corrected to userInput.

    for word in wordsToCheck: #Check every word in the provided file
        if not word in knownWords: # If the word is UNKNOWN, show it to the user with a suggestion(or not)
            
            # Suggest words in decreasing order of mistakes correction.
            if word in mistakes: #Check if there is a suggestion for that potentially misspelled word

                mistakes[word] = sortDecreasing(mistakes[word]) # Sort the list in decreasing order
                suggestion = '['
                num = 0
                for value in mistakes[word]:
                    if num > 0:
                        suggestion += ', '
                    suggestion+= f'{value[0]}' # Show suggestion(s)
                    knownCorrection.add(value[0]) # Add word to set
                    num+=1 #Add more than one suggestion if needed
                suggestion += ']'
            else: # If not, display 'no  suggestions'
                suggestion = '[no suggestions]' 


            print(f'Potential mistake: {word}\t{suggestion}')
            userInput = input('Action:')
            userInput = userInput.lower()
            

            # If user clicks enter key
            if userInput == "": 
                knownWords.append(word) #update dictionary
                if word in mistakes:# If the word was listed as misspelled, remove it.
                    mistakes.pop(word)
                returnedValue['myWords'].append(word) # Add the word to the dictionary
            
            # Otherwise, add the correct spelling to dictionary of mistakes
            else:
                if mistakeOccurrence.get(word) == None: # If it is the FIRST appearance of the mistake in the word
                    mistakeOccurrence[word] = 1 # Create a key/value for that mistake
                else:
                    mistakeOccurrence[word] +=1

                if numCorrections.get(userInput) == None: #If it is the FIRST time the user enters this correction
                    numCorrections[userInput] = 1 # Create key/value for that correction
                    mistakeOccurrence[userInput] = [] # Create a list to keep track of which mistake gets corrected
                else:
                    numCorrections[userInput] +=1

                mistakeOccurrence[userInput].append(mistakeOccurrence[word]) # Record which mistake gets corrected to what.

                # If it is the first appearance of the mistake in the text.
                if mistakes.get(word) == None:
                    mistakes[word] = []
                    mistakes[word].append( (userInput, mistakeOccurrence[word],mistakeOccurrence[userInput]) ) # Add tuple to list for that mistake
                else: # If userInput was entered earlier 
                    for i in range(len(mistakes[word])):
                        if mistakes[word][i][0] == userInput: # Update the tuple in the list
                            mistakes[word][i] = (userInput,numCorrections[userInput],mistakeOccurrence[userInput])
                    
                    if not userInput in knownCorrection: # If userInput is not in my known mistakes.
                        mistakes[word].append((userInput, 1 ,mistakeOccurrence[userInput])) # add tuple to the list
                        knownCorrection.add(userInput) # add known correction.
    
    for word in prevMistakes:
        for i in range(len(prevMistakes[word])):
            thisCorrection = prevMistakes[word][i][0]
            if thisCorrection in numCorrections:
                numCorrections[thisCorrection] += prevMistakes[word][i][1] # Add the previous number of correction to the new number

    for word in mistakes:
        for i in range(len(mistakes[word])):
            if mistakes[word][i][0] in knownCorrection:
                theWord = mistakes[word][i][0]
                mistakes[word][i] = (theWord, numCorrections[theWord], mistakeOccurrence[theWord]) # Update the number of corrections at the end using previous data (if present).

    return returnedValue # Return dictionary

def save(result:dict, originalText = '', fileName = ''):
    '''
    Updates the data in mywords.txt and mymistakes.txt if present.

    If the user provides a file to save data, this function creates a file with the given name and 
    writes new data to it by sending the parameters originalText and fileName to another function called replaceMistakes()
    that will write data to a new file.

        Parameters:  result (dict) is a dictionary with the data collected from spell, originalText(str) [Optional] is the entire file loaded in load() as a string, fileName(str) [Optional] is the file name given by user. 
    
        Post-condition: writes data to mywords.txt, mymistakes.txt and fileName if applicable.
    '''
    myWords = result.get('myWords') 
    myMistakes = result.get('mistakes')

    if len(myWords) > 0: # Rewrite or create mywords.txt file
        line = ''
        # Check if the file exists
        try:
            f = open('mywords.txt')
            line = f.readline() # Check if the file is empty
            f.close
        except FileNotFoundError:
            pass
        
        f = open('mywords.txt', 'a') # Reopen file for writing

        if line != '': # If the file is NOT empty
            f.write('\n') # Append new words to next line.
        for i in range (len(myWords)):
            if i != len(myWords)-1:
                f.write(myWords[i] + '\n')# Write a word per line.
            else:
                f.write(myWords[i]) # Don't add a line if it's the last word.
        f.close()

    # If mistakes were spotted and recorded, save them to the mistakes file or append to the previous file.
    try:
        if fileName != '': # If a filename is given 
            replaceMistakes(originalText, fileName, myMistakes) # Update the text by replacing misspelled words with corrections.
        
        mistakeFile = open('mymistakes.txt', 'w') # Open file for writing
        for key in myMistakes:
            mistakeFile.write(key + ', ') # Add the mistakes to the mistakeFile
            for i in range (len(myMistakes[key])): # iterate through tuple in my list
                tup = myMistakes[key][i]
                if i != 0:
                    mistakeFile.write(', ') # add a comma after first word
                
                mistakeFile.write(f'{tup[0]}, {tup[1]}') # Add word and number of corrections to line in file.

            mistakeFile.write('\n')
        mistakeFile.close()

    except IOError:
        print('There was an error reading or writing from the file. Please provide correct file name or review code.')

def replaceMistakes(originalText:str, newFile:str, misspelledData):
    '''
    Saves the mistakes and their data(if present) to a newFile provided by user.
        This function replaces the misspelled words with the appropriate corrections as provided by the user. 
    '''
    myMistakes = misspelledData

    wordList = originalText.split()
    for key in myMistakes: # Iterate through every misspelled word in dictionary
        correctedN = 0 # This variable keeps track of the occurrence of the misspelled word to correct the right words.
        
        for word in wordList: # Go through every word in the text that was first loaded
            word = word.split('.')[0] # Omit period
            if word == key: 
                correctedN +=1  
                for correctWord in myMistakes[key]:
                    if correctedN in correctWord[2]: # Check if it is the correct 
                        originalText = originalText.replace(key, correctWord[0],1) # Correct the previous file with the correct words if needed.
    
    f = open(newFile, 'w') #open file for writing
    f.write(originalText) # write modified text to file
    f.close()


def main():
    '''
    The main function function runs the program.

        - It first looks for three files(last two are optional) and returns the data needed when functions are called.
        - A conditional loop prompts the user for a command until they enter "quit". 
            Three prompts are expected: load fileName, spell, save fileName.
        - Each prompt calls a function to execute its intended referend.
        - If the user quits without saving their changes to a file, only mistakes.txt and mywords.txt are updated.

    '''
    words = []
    originalText = ''
    result = dict()

    myWords, mistakes = getKnownWords('words.txt', 'mywords.txt', 'mymistakes.txt') # Look for the THREE FILES
    savable = False
    saved = False
    canSpell = False
    command = input("Enter command: ").lower() # Prompt user for a command
    
    while command != "quit": # Continously prompt user until they quit the program.
        sentence = command.split() # Get words in sentence.
        try:
            if sentence[0].lower() == "load": # LOAD
                words, originalText = load(sentence[1])
                canSpell = True # user is now allowed to call spell function
                saved = False

            elif sentence[0].lower() == "spell" and len(sentence) ==1: # SPELL
                if canSpell == True:
                    if len(mistakes) > 0: # If mymistakes.txt was present 
                        result = spell(words,myWords, mistakes)
                    else:
                        result = spell(words, myWords)
                    
                    for key in result['mistakes']:
                        result['mistakes'][key] = sortDecreasing(result['mistakes'][key]) # Sort the corrections in DECREASING order.
                    savable = True # user can now call save function
                else:
                    print('You must first load a file before you can spell.')

            elif sentence[0].lower() == "save": # SAVE
                if savable == True:
                    if len(sentence) == 2: # Save mymistakes.txt, mywords.txt, and the provided file
                        save(result, originalText, sentence[1])
                    elif len(sentence) ==1: # Save mymistakes.txt and mywords.txt
                        save(result)
                    saved = True
                else:
                    print('You must first load and spell before you can save.')

            else: # If the input is invalid.
                raise Exception
        except Exception:
            print("Invalid input. Please enter a valid command.")

        command = input("Enter command: ")
        command = command.lower()

    # When the loop ends, save content file if possible
    if savable == True and saved == False:
        save(result)

###############
# Helper functions below
##############

def sortDecreasing(List:list):
    '''
    Sorting algorithm for sorting corrections from most frequent to least frequent. Similar to insertion sort. 
    '''
    biggest = 0 # variable number
    for i in range(len(List)):
        biggest = List[i]
        k = i+1
        index = 0

        while k <= len(List)-1:  # As long as the end of the list hasn't been reached 
            if List[k][1] > biggest[1]: # Check if the number at this index is greater than the prev biggest number.
                biggest = List[k] # Make this the biggest number
                index = k # record index
            k+=1

        # Swap them
        if index != 0: # If a number was found to be greated
            List[i], List[index] = List[index], List[i]
    return List

def getKnownWords(words:str, myWords, commonMistakes):
    '''
    When the program starts,  this function looks for three file: words.txt(Always there),
    mywords.txt(may not be there), and mistakes.txt(may not be there).

        From words.txt, it creates a list where all the known spelling of words are stored and returns it.

        From mywords.txt, it adds to the list of known words the personal words added by the user or programmer.

        From mistakes.txtt, it stores spelling(s) of misspelled words to potentially display suggestions to user.
    '''
    
    mistakes = {} # Create dictionary
    allWords = []

    # Read First file
    try:
        f = open(words)
        
        for line in f:
            size = len(line)-1
            if line[size:size+1] == '\n': # If the last character is the escape sequence '\n'
                line = line[:size] # Discard it.
            allWords.append(line) # Add the word to the list of known words.
        f.close()
    except IOError as error:
        print(error)
    
    # Read Second file
    try:
        f2 = open(myWords)

        for line in f2:
            size = len(line)-1
            if line[size:size+1] == '\n': # If the last character is the escape sequence '\n'
                line = line[:size] # Discard it.
            allWords.append(line) # Add the word to the list of known words. 
        f2.close()
    except IOError as error:
        pass

    # Read Third file
    try:
        f3 = open(commonMistakes) # Open

        for line in f3:
            List = line.split(',')
            mistakes[List [0]] = [] 
            for i in range(1, len(List), 2):
            # Add a key whose value is a list of tuples of mistake correction and the number of times they were entered.
                mistakes[List[0]].append((List[i].strip(), int(List[i+1].strip()))) 
        f3.close()
    except IOError as error:
        pass

    return allWords, mistakes

# main guard
if __name__ == "__main__":
    main()