import spacy
import textacy

nlp = spacy.load('en')


# doc = nlp(u'London is a big city in the United Kingdom.')



def get_pattern(doc, pattern):
    all_matches = []
    for t, token in doc:
        if pattern[0] == token.tag_:
            matches = True
            for i, part in pattern:
                if part != doc[t + i].tag_:
                    matches = False
                    break
            if matches:
                all_matches.append(doc[t:len(pattern)])

    return all_matches


def get_sentences(line):
    doc = nlp(line)
    sentences = [sent.string.strip() for sent in doc.sents]
    return sentences


def important_phrases(sentence):
    phrases = []
    doc = nlp(sentence)
    tags = []
    for token in doc:
        # print("Token: ", token.tag_, token.pos_, token)
        tags.append(token.tag_)
    heads = {}
    for np in doc.noun_chunks:
        head = np.root.head.text
        phrases.append(np.text)
        selectedHead = {}
        if head in heads:
            selectedHead = heads[head]

        selectedHead[np.root.dep_] = np.text
        heads[head] = selectedHead

    return {
        'phrases': phrases,
        'tags': tags
    }


def parse_sentence(sentence):
    tag_map = {}
    important = important_phrases(sentence)
    # for phrase in important['phrases']:
    #     print(phrase)
    tags = important['tags']
    # print("\n")
    smaller_tags = []
    current_tag = []
    for tag in tags:
        if tag in ["JJ", ",", "TO", "."]:
            if len(current_tag) > 0:
                smaller_tags.append(current_tag)
            current_tag = []
        else:
            current_tag.append(tag)
    if len(current_tag) > 0:
        smaller_tags.append(current_tag)
    for smaller_tag in smaller_tags:
        tag_hash = " ".join(smaller_tag)
        if tag_hash not in tag_map:
            tag_map[tag_hash] = 1
        else:
            tag_map[tag_hash] += 1

    return tag_map


with open("abstracts.txt") as f:
    tag_map = {}
    lines = []
    for line in f:
        lines.append(line)

    for line in lines:
        sentences = get_sentences(line)

        for sentence in sentences:
            tags = parse_sentence(sentence)
            for tag in tags:
                if tag in tag_map:
                    tag_map[tag] += tags[tag]
                else:
                    tag_map[tag] = tags[tag]

    corpus = textacy.Corpus('en', lines)

    for doc in corpus:
        matches = textacy.extract.pos_regex_matches(doc, r'<PRON> <VERB> <DET>? <PRON>?')
        acronyms = textacy.extract.acronyms_and_definitions(doc)
        # semistructured_statements = textacy.extract.semistructured_statements(doc)
        subject_verb_object_triples = textacy.extract.subject_verb_object_triples(doc)
        key_terms_from_semantic_network = textacy.keyterms.key_terms_from_semantic_network(doc, 'lemma', 3)
        singlerank = textacy.keyterms.singlerank(doc)
        textrank = textacy.keyterms.textrank(doc)
        sgrank = textacy.keyterms.sgrank(doc)

        for sent in doc.sents:
            print(sent)
        print("====")
        print(acronyms)
        print("==subject_verb_object_triples==")
        for trip in subject_verb_object_triples:
            print(trip)
        print("==sgrank==")
        for sgr in sgrank:
            print(sgr)
        print("==singlerank==")
        for sgr in singlerank:
            print(sgr)
        print("==textrank==")
        for sgr in textrank:
            print(sgr)
        print("==key_terms_from_semantic_network==")
        for trip in key_terms_from_semantic_network:
            print(trip)
        print("==matches==")
        for match in matches:
            print(match)
        print("\n")

    vectorizer = textacy.Vectorizer(
        weighting='tfidf', normalize=True, smooth_idf=True,
        min_df=3, max_df=0.95)
    doc_term_matrix = vectorizer.fit_transform((
        doc.to_terms_list(
            ngrams=1,
            named_entities=True,
            as_strings=True
        ) for doc in corpus)
    )
    print(repr(doc_term_matrix))

    models = ['nmf', 'lda', 'lsa']
    for m in models:
        model = textacy.TopicModel(m, n_topics=10)
        model.fit(doc_term_matrix)
        doc_topic_matrix = model.transform(doc_term_matrix)
        print("==", m, "==")
        print(doc_topic_matrix.shape)
        for topic_idx, top_terms in model.top_topic_terms(vectorizer.id_to_term, top_n=10):
            print('topic', topic_idx, ':', '   '.join(top_terms))
