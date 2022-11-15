import re
import requests
from thefuzz import fuzz
from thefuzz import process
import json
import pandas as pd
import tkinter as tk
from tkinter import font

## Date: 9/11/22
## Written by Yaniv Tawily
## The Program:
# My purpose in writing the program is to compare the similar parts of the Tanakh,
# By that I mean that they are the same text in two different versions in the Tanakh.
# For example David's heroes who are shown in the II Samuel (ch 23) and in I Chronicles (ch 11).
# For the demonstration I used both of them in the program, but it can be used on other texts as well.
# The text I took from using the API library of Sefaria.
# I deliberately chose a Version with Ta'amei Hamikra and Nikkud so i can show the use of regular expressions.
# I scanned the two sections of text using fuzzy matching to find the different words between the two texts.
# Also, please check the image I added in git which explains the program well.
# ps sorry about the GUI this is what I can do on short notice

root = tk.Tk()


def printTextA(text, colours):
    for index, word in enumerate(text):
        tk.Label(root, text=word, fg=colours[index]).grid(column=10-(index % 10), row=int((index / 10) + 5), sticky=tk.W)


def printTextB(text, colours):
    for index, word in enumerate(text):
        tk.Label(root, text=word, fg=colours[index]).grid(column=20-(index % 10), row=int((index / 10) + 5))


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


# Remove Nikkud from string (start from 1456 to not skip Ta'amei Hamikra)
def removeNikkud(my_string):
    return ''.join(['' if 1425 <= ord(c) <= 1479 and c != '־' else c for c in my_string])


# Load the 2 texts from Sefaria API
response = requests.get("http://www.sefaria.org/api/texts/II_Samuel.23")
response_2 = requests.get("http://www.sefaria.org/api/texts/I_Chronicles.11")

if response.status_code != 200 or response_2.status_code != 200:
    print("the texts didn't arrived well")
else:
    print("the texts arrived")
    TextA = response.json()['he']
    TextB = response_2.json()['he']
    TextA = str(TextA)
    TextB = str(TextB)

    #### Regular expressions to make the text more useable for matching
    # Clear any type of english text or ant signs
    TextA = re.sub(r'([a-zA-z0-9]*)|([/<>"=,:\'])*|([׃])',"",TextA)
    TextB = re.sub(r'([a-zA-z0-9]*)|([/<>"=,:\'])*|([׃])',"",TextB)
    # Remove open or close parashiyot
    TextA = re.sub(r'\{[פס]\}', "", TextA)
    TextB = re.sub(r'\{[פס]\}', "", TextB)
    # Remove Ketiv
    TextA = re.sub(r'\(([א-ת])*\)', "", TextA)
    TextB = re.sub(r'\(([א-ת])*\)', "", TextB)
    # Remove Nikkud
    TextA = removeNikkud(TextA)
    TextB = removeNikkud(TextB)
    # Remove Dash -
    TextA = re.sub(r'[\-־]+', " ", TextA)
    TextB = re.sub(r'[\-־]+', " ", TextB)
    # Remove extra spaces
    TextA = re.sub(r'\s+', " ", TextA)
    TextB = re.sub(r'\s+', " ", TextB)
    print(TextA)
    print(TextB)

    ## Print the matching ratio of the texts
    label1 = tk.Label(root,text="hi, This is program comparing II Samuel (ch 23) and in I Chronicles (ch 11)\n there is " + str(fuzz.ratio(TextA, TextB)) + " match between them").grid(column=10, row=0)
    print(fuzz.ratio(TextA, TextB))
    print(fuzz.token_set_ratio(TextA, TextB))

    ## Make preparation for fuzzy matching
    TextA = TextA.split()
    TextB = TextB.split()
    TextBLen = len(TextB)
    ColoursTA = ['red' for i in range(len(TextA))]
    ColoursTB = ['red' for i in range(len(TextB))]
    CounterTB = int(0)
    KeepGoing = True

    # The required matching percentage
    HardLook = 90

    ## Comparing words in text A versus text B using fuzzy matching
    for indexS, S in enumerate(TextA, start = 0):
        if CounterTB < TextBLen:
            if fuzz.ratio(S, TextB[CounterTB]) > HardLook:
                ColoursTA[indexS] = "blue"
                ColoursTB[CounterTB] = "blue"
                CounterTB += 1
            else:
                OldCounter = CounterTB
                KeepGoing = True

                tempColorC = ColoursTB
                while CounterTB < TextBLen and KeepGoing:
                    if fuzz.ratio(S, TextB[CounterTB]) > HardLook:
                        ColoursTA[indexS] = "blue"
                        ColoursTB[CounterTB] = "blue"
                        KeepGoing = False
                        CounterTB += 1
                    else:
                        CounterTB += 1
                ColoursTB = tempColorC
                CounterTB = OldCounter + 1

    ## Pass the result of the comparison to Tkinter
    printTextA(TextA, ColoursTA)
    printTextB(TextB, ColoursTB)

    ## Open GUI
    tk.mainloop()

