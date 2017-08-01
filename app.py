from apistar import App, Include, Route
from apistar.docs import docs_routes
from apistar.statics import static_routes

import spacy  # See "Installing spaCy"

nlp = spacy.load('en')  # You are here.


def parseSentence(sentence=None):
    if sentence is None:
        return {'message': 'Welcome to NLP Api!'}
    doc = nlp(sentence)

    partsOfSpeech = [{
        'token': word.text,
        # 'lemma': word.lemma,
        # 'tag': word.tag,
        # 'pos': word.pos,
        'lemma': word.lemma_,
        'tag': word.tag_,
        'pos': word.pos_,
    } for word in doc]

    dependency = [{
        'token': np.text,
        'root': np.root.text,
        'dependency': np.root.dep_,
        'head': np.root.head.text,
    } for np in doc.noun_chunks]

    entities = [{
        'token': ent.text,
        'label': ent.label_,
    } for ent in doc.ents]

    print(entities)

    return {
        'sentence': sentence,
        'pos': partsOfSpeech,
        'dependency': dependency,
        'entities': entities,
    }


routes = [
    Route('/pos', 'GET', parseSentence),
    Include('/docs', docs_routes),
    Include('/static', static_routes)
]

app = App(routes=routes)
