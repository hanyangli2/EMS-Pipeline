import spacy
import scispacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from negspacy.negation import Negex


# lemmatizing the notes to capture all forms of negation(e.g., deny: denies, denying)
#def lemmatize(note, nlp):
 #   doc = nlp(note)
  #  lemNote = [wd.lemma_ for wd in doc]
   # return " ".join(lemNote)


# adding a new pipeline component to identify negation
def neg_model(nlp_model):
    nlp = spacy.load(nlp_model, disable=['parser'])
    nlp.add_pipe('sentencizer')
    nlp.add_pipe("negex", config={"ent_types": ["DISEASE", "NEG_ENTITY"]})
    return nlp


def negation_handling(nlp_model, note, neg_model):
    results = []
    nlp = neg_model(nlp_model)
    note = note.split(".")  # sentence tokenizing based on delimeter
    note = [n.strip() for n in note]  # removing extra spaces at the begining and end of sentence
    for t in note:
        doc = nlp(t)
        for e in doc.ents:
            rs = str(e._.negex)
            if rs == "True":
                results.append(e.text)
    return results  # list of negative concepts from clinical note identified by negspacy


# function to identify span objects of matched negative phrases from clinical note
def match(nlp, terms, label):
    patterns = [nlp.make_doc(text) for text in terms]
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add(label, None, *patterns)
    return matcher


# replacing the labels for identified negative entities
def overwrite_ent_lbl(matcher, doc):
    matches = matcher(doc)
    seen_tokens = set()
    new_entities = []
    entities = doc.ents
    for match_id, start, end in matches:
        if start not in seen_tokens and end - 1 not in seen_tokens:
            new_entities.append(Span(doc, start, end, label=match_id))
            entities = [
                e for e in entities if not (e.start < end and e.end > start)
            ]
            seen_tokens.update(range(start, end))
            doc.ents = tuple(entities) + tuple(new_entities)
    return doc


def find_negation(sent_text):
    nlp0 = spacy.load("en_core_web_sm")
    nlp1 = spacy.load("en_ner_bc5cdr_md")

#    lem_clinical_note = lemmatize(sent_text, nlp0)

    #negated_list = negation_handling("en_ner_bc5cdr_md", lem_clinical_note, neg_model)
    negated_list = negation_handling("en_ner_bc5cdr_md", sent_text, neg_model)
    return negated_list;


def main():
    clinical_note = "Patient is a 60 year old having difficulty in breathing. \
    Not diabetic. \
    He feels that he has been in good health until this current episode. \
    Appetite - good. No chest pain. \
    No weight loss or episodes of stomach pain. \
    Hypertension absent.\
    "
    
    negated_values = find_negation(clinical_note)

    print(negated_values)

if __name__ == "__main__":
    main()
