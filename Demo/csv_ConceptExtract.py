from __future__ import absolute_import, division, print_function
from classes import SpeechNLPItem, GUISignal
from Form_Filling import textParse2
from GUI import MainWindow
import subprocess
import csv
import time
import time

BETWEEN_CHARACTERS_PAUSE = .006
BETWEEN_WORDS_PAUSE = .01
BETWEEN_SENETENCES_PAUSE = 0.1
COMMA_PAUSE = .03

concept_num = 0

def get_concept_num():
    global concept_num
    return concept_num

def set_concept_num(value):
    global concept_num
    concept_num = value

def TextSpeech(Window, SpeechToNLPQueue, text_input):
    text = text_input

    # Create GUI Signal Object
    SpeechSignal = GUISignal()
    SpeechSignal.signal.connect(Window.UpdateSpeechBox)

    MsgSignal = GUISignal()
    MsgSignal.signal.connect(Window.UpdateMsgBox)

    ButtonsSignal = GUISignal()
    ButtonsSignal.signal.connect(Window.ButtonsSetEnabled)

    # Open the CSV file
    with open(text, 'r') as file:
        # Create a CSV reader object
        reader = csv.reader(file)
        # Iterate over the rows of the CSV file
        for row in reader:
            # Print the string values for each row
            text = row[0]
            #SpeechSignal.signal.connect(Window.ClearWindows())
            print("New Text Entry")
            print(text)
            # Break into sentences
            auto_chunk = True
            if auto_chunk:
                dummy12 = text
                print("PART 1")
                print(dummy12)
                dummy12 = dummy12.replace('\r', '').replace('\n', '')
                print("PART 2")
                print(dummy12)
                dummyP2 = dummy12.replace(' ', '%20')
                print("PART 3")
                print(dummyP2)
                dummyP3 = dummyP2.replace('\'', '%27')
                print("PART 4")
                print(dummyP3)
                dummyP = dummyP3.replace('&', '%26')
                print("PART 5")
                print(dummyP)
                part1 = 'curl -d text=' + dummyP + ' http://bark.phon.ioc.ee/punctuator'
                print("PART 6")
                print(part1)
                op = subprocess.getstatusoutput(part1)
                print("OP")
                print(op)
                output = op[1].rsplit('\n', 1)[1]
                sentsList = textParse2.sent_tokenize(output)  # final sentences
            else:
                sentsList = text.split("###")

            # Stream text
            num_chars_printed = 0
            for sentence in sentsList:
                for i, character in enumerate(sentence):
                    QueueItem = SpeechNLPItem(sentence[: i + 1], False, 0, num_chars_printed, 'Speech')
                    SpeechSignal.signal.emit([QueueItem])
                    if character == " ":
                        time.sleep(BETWEEN_WORDS_PAUSE)
                    elif character == ",":
                        time.sleep(COMMA_PAUSE)
                    elif character == ".":
                        time.sleep(BETWEEN_SENETENCES_PAUSE)
                    else:
                        time.sleep(BETWEEN_CHARACTERS_PAUSE)
                    num_chars_printed = len(sentence[: i + 1])

                    if Window.stopped == 1:
                        print('Text Speech Tread Killed')
                        QueueItem = SpeechNLPItem(sentence[: i + 1], True, 0, num_chars_printed, 'Speech')
                        SpeechSignal.signal.emit([QueueItem])
                        SpeechToNLPQueue.put(QueueItem)
                        return

                QueueItem = SpeechNLPItem(sentence, True, 0, num_chars_printed, 'Speech')
                SpeechSignal.signal.emit([QueueItem])
                SpeechToNLPQueue.put(QueueItem)
                num_chars_printed = 0


            time.sleep(200)
            set_concept_num(get_concept_num() + 1)
            print("CONCEPT NUM GETTER SIDE")
            print(concept_num)
            print("Text File Speech Thread Started")
            SpeechSignal.signal.connect(Window.ClearWindows)
            # Clean up and end thread
            MsgSignal.signal.emit(["Transcription of text file complete!"])
            ButtonsSignal.signal.emit([(Window.StartButton, True), (Window.ComboBox, True), (Window.ResetButton, True)])




