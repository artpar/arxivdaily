import spacy

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
    for line in f:
        sentences = get_sentences(line)

        for sentence in sentences:
            tags = parse_sentence(sentence)
            for tag in tags:
                if tag in tag_map:
                    tag_map[tag] += tags[tag]
                else:
                    tag_map[tag] = tags[tag]
        print("\n\n")

    for tag in tag_map:
        print(tag_map[tag], tag)
