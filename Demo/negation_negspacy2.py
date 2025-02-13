import spacy
from negspacy.negation import Negex

#Corpus on which the model is trained
bc5_model = "en_ner_bc5cdr_md"

#Sample clinical note
clinical_note="Patient is a 60 year old having difficuly in breathing. \
Not diabetic. \
He feels that he has been in good health until this current episode. \
Appetite - good. No chest pain. \
No weight loss or episodes of stomach pain. \
Hypertension absent.\
"


# Adding a new pipeline component to identify negation

def negation_model(nlp_model):
    nlp = spacy.load(nlp_model)
    nlp.add_pipe("negex", config={"ent_types": ["DISEASE", "CHEMICAL"]})
    return nlp


# Identifying negation entities

def get_negation_entities(nlp_model, text, negation_model):
    results = []
    # Set up negex in the pipeline
    nlp = negation_model(nlp_model)
    # Split up the note into sentences (use . as the delimiter)
    text = text.split(".")

    # Aggregate all the negative entities in a list
    for sentence in text:
        doc = nlp(sentence)
        for e in doc.ents:
            test = str(e._.negex)
            if test == "True":
                results.append(e.text)
    return results

def find_neg(sent_text):
    # Get the list of negative entities from clinical note identified
    final_results = get_negation_entities(bc5_model, sent_text, negation_model)
    # Print the list of negative identities
    print(final_results)


def main():
    # Get the list of negative entities from clinical note identified
    final_results = get_negation_entities(bc5_model, clinical_note, negation_model)
    # Print the list of negative identities
    print(final_results)


if __name__ == "__main__":
    main()
