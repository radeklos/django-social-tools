
def get_containing_words(words_list, content):
    normalise = lambda w: w.lower()
    normalized_content = normalise(content)

    found_words = set()
    for word in words_list:
        if normalise(word).strip() in normalized_content:
            found_words.add(word)
    return found_words
