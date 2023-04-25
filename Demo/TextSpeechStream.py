from __future__ import absolute_import, division, print_function
from timeit import default_timer as timer
import time
import numpy as np
from classes import SpeechNLPItem, GUISignal
from Form_Filling import textParse2
import subprocess

BETWEEN_CHARACTERS_PAUSE = .006
BETWEEN_WORDS_PAUSE = .01
BETWEEN_SENETENCES_PAUSE = 0.1
COMMA_PAUSE = .03


def TextSpeech(Window, SpeechToNLPQueue, textfile_name):
    print("Entered TextSpeech")

    # Create GUI Signal Object
    SpeechSignal = GUISignal()
    SpeechSignal.signal.connect(Window.UpdateSpeechBox)

    MsgSignal = GUISignal()
    MsgSignal.signal.connect(Window.UpdateMsgBox)

    ButtonsSignal = GUISignal()
    ButtonsSignal.signal.connect(Window.ButtonsSetEnabled)

    #  Text_File = open('/home/harry/Documents/recording_0_text.txt', "rb")

    # text = ""
    # for line in Text_File.readlines():
    #    text += line
    # counter = 0

    text = "We'Re dispatch for an adult female complaining of chest pain that sort of approximately 15 minutes. Prior to our arrival, we found her in her bedroom, laying on laying on her back. She did not appear to be any in any acute distress and choosing could color without any increase work of breathing. She describes the pain of sharp, constant, substernal, localized and non radiating and reproducible to palpation. The pain is also works on inspiration. She says the pain is at about 10 out of 10. Patient currently denies any associate symptoms such as nausea trauma, pregnancy or difficulty. Breathing. However, patient does have a history of deep vein thrombosis he's in her legs, for which is currently taking Lovenox Patient is currently in good color, breathing, normally except she's a mildly anxious or at least appears to be aspirin was not administered. Due to the patient's known allergy, her vital signs were as follows: she had a 12-lead perform I'm showing no stemi and a normal sinus rhythm without any other ectopy her blood pressure is 126 over 77 she is a GCS of 15 blood glucose of 82 oxygen saturation of 100 respirator respirations are 18 times a minute with a heart rate of 58 and Ivy has been established and locked with normal saline and that's it"

    # Break into sentences
    auto_chunk = True
    if auto_chunk:
        dummy12 = text
        dummy12 = dummy12.replace('\r', '').replace('\n', '')
        dummyP2 = dummy12.replace(' ', '%20')
        dummyP3 = dummyP2.replace('\'', '%27')
        dummyP = dummyP3.replace('&', '%26')
        part1 = 'curl -d text=' + dummyP + ' http://bark.phon.ioc.ee/punctuator'
        op = subprocess.getstatusoutput(part1)
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
            if (character == " "):
                time.sleep(BETWEEN_WORDS_PAUSE)
            elif (character == ","):
                time.sleep(COMMA_PAUSE)
            elif (character == "."):
                time.sleep(BETWEEN_SENETENCES_PAUSE)
            else:
                time.sleep(BETWEEN_CHARACTERS_PAUSE)
            num_chars_printed = len(sentence[: i + 1])

            if (Window.stopped == 1):
                print('Text Speech Tread Killed')
                QueueItem = SpeechNLPItem(sentence[: i + 1], True, 0, num_chars_printed, 'Speech')
                SpeechSignal.signal.emit([QueueItem])
                SpeechToNLPQueue.put(QueueItem)
                return

        QueueItem = SpeechNLPItem(sentence, True, 0, num_chars_printed, 'Speech')
        SpeechSignal.signal.emit([QueueItem])
        SpeechToNLPQueue.put(QueueItem)
        num_chars_printed = 0

    # Clean up and end thread
    MsgSignal.signal.emit(["Transcription of text file complete!"])
    ButtonsSignal.signal.emit([(Window.StartButton, True), (Window.ComboBox, True), (Window.ResetButton, True)])
