import pyConTextNLP.pyConText as pyConText
import pyConTextNLP.itemData as itemData
import re
import networkx as nx
import os

PYCONTEXTNLP_MODIFIERS = '/home/harry/Downloads/EMS-Pipeline/Demo/EMS-Pipeline-pycontextnlp-negation-detector/data/pycontextnlp_modifiers.yml'
PYCONTEXTNLP_TARGETS = '/home/harry/Downloads/EMS-Pipeline/Demo/EMS-Pipeline-pycontextnlp-negation-detector/data/pycontextnlp_targets.yml'


def pycontext_findneg(sent_text):
    modifiers = itemData.get_items(PYCONTEXTNLP_MODIFIERS)
    targets = itemData.get_items(PYCONTEXTNLP_TARGETS)
    markup = pyConText.ConTextMarkup()
    markup.setRawText(sent_text.lower())
    # print(markup)
    # print(len(markup.getRawText()))
    markup.cleanText()
    # print(markup)
    # print(len(markup.getText()))
    markup.markItems(modifiers, mode="modifier")
    markup.markItems(targets, mode="target")
    # for node in markup.nodes(data=True):
    #     print(node)
    markup.pruneMarks()
    # for node in markup.nodes(data=True):
    #     print(node)
    markup.applyModifiers()

#    for edge in markup.edges():
#       print(edge)

    list = [];
    for edge in markup.edges():
        list.append(edge)
    return list


def negated(value):
    bool = (str(value[0][0].getCategory()) == '[\'probable_negated_existence\']' or str(value[0][0].getCategory()) == '[\'definite_negated_existence\']')
    if bool:
        return False
    else:
        return True


def main():
    text = "Patient currently denies any associate symptoms such as nausea, trauma, pregnancy or difficulty."
    tags = pycontext_findneg(text)
    dict = {}
    i = 0
    for x in tags:
        category = re.sub(r'[^a-zA-Z]', '', str(tags[i][1].getCategory()))
        dict[str(category)] = negated(tags)
        i += 1
    print(dict)




if __name__ == "__main__":
    main()
