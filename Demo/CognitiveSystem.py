from __future__ import absolute_import, division, print_function
from py_trees import blackboard
from six.moves import queue
import py_trees
import behaviours_m as be
from py_trees.blackboard import Blackboard
from tqdm import tqdm as tqdm

from classes import SpeechNLPItem, GUISignal
import threading
import text_clf_utils as utils
from ranking_func import rank
from csv_ConceptExtract import concept_num, get_concept_num
from Form_Filling import textParse2
from operator import itemgetter
import subprocess
import re
import csv

#added 3/18
import nltk
nltk.download('punkt')
#--

# ============== Cognitive System ==============
from behaviours_m import blackboard
blackboard.tick_num = 0

# Cognitive System Thread


def CognitiveSystem(Window, SpeechToNLPQueue):
    # Create GUI signal objects
    SpeechSignal = GUISignal()
    SpeechSignal.signal.connect(Window.UpdateSpeechBox)

    ConceptExtractionSignal = GUISignal()
    ConceptExtractionSignal.signal.connect(Window.UpdateConceptExtractionBox)

    # Initialize BT framework parameters
    exec(open("./bt_parameters.py").read())

    # Setup BT Framework
    #blackboard = Blackboard()
    global blackboard
    root = py_trees.composites.Sequence("Root_1")
    IG = be.InformationGathering()
    TC = be.TextCollection()
    V = be.Vectorize()
    PS = be.ProtocolSelector()
    root.add_children([TC, IG, V, PS, be.protocols])  # be.protocols
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.setup()
    Concepts_Graph = dict()
    SpeechText = ""
    NLP_Items = []
    Tick_Counter = 1

    while True:

        # Get queue item from the Speech-to-Text Module
        received = SpeechToNLPQueue.get()
        print("Received chunk")

        if(received == 'Kill'):
            print("Cognitive System Thread received Kill Signal. Killing Cognitive System Thread.")
            break

        if(Window.reset == 1):
            print("Cognitive System Thread Received reset signal. Killing Cognitive System Thread.")
            return

        # If item received from queue is legitmate
        else:
            #sentsList = [received.transcript]

            # Use online tool to find sentence boundaries
            dummy12 = received.transcript
            dummy12 = dummy12.replace('\r', '').replace('\n', '')
            dummyP2 = dummy12.replace(' ', '%20')
            dummyP3 = dummyP2.replace('\'', '%27')
            dummyP = dummyP3.replace('&', '%26')
            part1 = 'curl -d text='+dummyP+' http://bark.phon.ioc.ee/punctuator'
            op = subprocess.getstatusoutput(part1)
            print("op:  ", op)
            output = op[1].rsplit('\n', 1)[1]
            sentsList = textParse2.sent_tokenize(output)  # final sentences

            def print_tree(tree):
                print(py_trees.display.unicode_tree(root=tree.root, show_status=True))

            # Processes each chunk/sentence
            PunctuatedAndHighlightedText = ""
            for idx, item in enumerate(sentsList):

                blackboard.text = [item]
                behaviour_tree.tick_tock(
                    period_ms=50,
                    number_of_iterations=1,
                    pre_tick_handler=None,
                    post_tick_handler=print_tree)

                pr, sv_s, s = TickResults(Window, NLP_Items)

                PunctuatedAndHighlightedTextChunk = item

                for sv in sv_s:
                    if(sv[5] == Tick_Counter):  # if new concept found in this tick
                        try:
                            i = re.search(r'%s' % sv[3], PunctuatedAndHighlightedTextChunk).start()
                            PunctuatedAndHighlightedTextChunk = str(PunctuatedAndHighlightedTextChunk[:i] + '<span style="background-color: #FFFF00">' + PunctuatedAndHighlightedTextChunk[i:i + len(
                                sv[3])] + '</span>' + PunctuatedAndHighlightedTextChunk[i + len(sv[3]):])
                        except Exception as e:
                            pass

                PunctuatedAndHighlightedText += PunctuatedAndHighlightedTextChunk + " "
                Tick_Counter += 1

                if(Window.reset == 1):
                    print("Cognitive System Thread Received reset signal. Killing Cognitive System Thread.")
                    return

            PunctuatedAndHighlightedText = '<b>' + PunctuatedAndHighlightedText + '</b>'
            SpeechSignal.signal.emit([SpeechNLPItem(
                PunctuatedAndHighlightedText, received.isFinal, received.confidence, received.numPrinted, 'NLP')])


# Function to return this recent tick's results
def TickResults(Window, NLP_Items):
    # Number of empty rows to add to the CSV file

    # print(NLP_Items)
    ConceptExtractionSignal = GUISignal()
    ConceptExtractionSignal.signal.connect(Window.UpdateConceptExtractionBox)

    ProtocolSignal = GUISignal()
    ProtocolSignal.signal.connect(Window.UpdateProtocolBoxes)

    #blackboard = Blackboard()
    global blackboard
    protocol_candidates = []
    signs_and_vitals = []
    suggestions = []

    print("===============================================================")

    # ======= Top 3 protocol candidates
    print("\n======= Top 3 protocol candidates:")
    for p in blackboard.protocol_flag:
        print(p, blackboard.protocol_flag[p])
        binary = blackboard.protocol_flag[p][0]
        confidence = blackboard.protocol_flag[p][1]
        if(binary):
            try:
                if(confidence != 'nan' and float(confidence) > 0.0):
                    protocol_candidates.append((str(p), confidence))
            except Exception as e:
                pass

    # Sort by confidence and take top 3
    protocol_candidates = sorted(protocol_candidates, key=itemgetter(1), reverse=True)[:3]

    # ======= Signs, symptoms, and vitals
    print("\n======= Signs, symptoms, and vitals:")
    for item in blackboard.Vitals:
        if len(blackboard.Vitals[item].content) > 0:
            content = (str(blackboard.Vitals[item].name).capitalize(), str(blackboard.Vitals[item].binary),
                       str(blackboard.Vitals[item].value), str(blackboard.Vitals[item].content),
                       str(round(blackboard.Vitals[item].score/1000, 2)), blackboard.Vitals[item].tick)
            print("content")
            print(content)
            signs_and_vitals.append(content)
            if(content not in NLP_Items):
                NLP_Items.append(content)

    for item in blackboard.Signs:
        if len(blackboard.Signs[item].content) > 0:
            content = (str(blackboard.Signs[item].name).capitalize(), str(blackboard.Signs[item].binary),
                       str(blackboard.Signs[item].value), str(blackboard.Signs[item].content),
                       str(round(blackboard.Signs[item].score/1000, 2)), blackboard.Signs[item].tick)
            print(content)
            signs_and_vitals.append(content)
            if(content not in NLP_Items):
                NLP_Items.append(content)

    # Sort by Tick
    signs_and_vitals = sorted(signs_and_vitals, key=itemgetter(5))
    #
    # # Read the CSV file into a list of rows
    # with open('csv_concepts.csv', 'r') as file:
    #     rows = list(csv.reader(file))
    # # Modify the value of the cell (row 2, column 3)
    # print("concept_num: ")
    # print(get_concept_num())
    # rows[get_concept_num()] = signs_and_vitals
    # # Write the modified list of rows back to the CSV file
    # with open('csv_concepts.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(rows)

    # ======= Suggestions
    print("\n======= Suggestions:")
    for key in blackboard.feedback:
        if blackboard.feedback[key] > 0.1:
            content = (str(key).capitalize(), str(round(blackboard.feedback[key], 2)))
            suggestions.append(content)
            print(content)

    # Sort by Concept
    suggestions = sorted(suggestions, key=itemgetter(1), reverse=True)

    # ========================== Create output strings formatted for readibility
    protocol_candidates_str = ""
    for i, p in enumerate(protocol_candidates):
        protocol_candidates_str += "(" + p[0] + ", <b>" + str(round(p[1], 2)) + "</b>)<br>"

    signs_and_vitals_str = ""
    for sv in NLP_Items:
        signs_and_vitals_str += "("
        for i, t in enumerate(sv):
            if(i != 3 and i != 4 and i != 5):
                signs_and_vitals_str += str(t)[0:len(str(t))] + ", "
            if(i == 4):
                signs_and_vitals_str += "<b>" + str(t)[0:len(str(t))] + "</b>, "
        signs_and_vitals_str = signs_and_vitals_str[:-2] + ")<br>"

    suggestions_str = ""
    for s in suggestions:
        suggestions_str += "(" + str(s[0]) + ", <b>" + str(s[1]) + "</b>)<br>"

    print("===============================================================")

    ProtocolSignal.signal.emit([protocol_candidates_str, suggestions_str])
    ConceptExtractionSignal.signal.emit([signs_and_vitals_str])

    return protocol_candidates, signs_and_vitals, suggestions

# Extract concept and calculate similarity
def pre_tick_handler(behaviour_tree):
    #blackboard = Blackboard()
    global blackboard
    blackboard.tick_num += 1
