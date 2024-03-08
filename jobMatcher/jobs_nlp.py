from nltk.corpus import stopwords, words
import numpy as np
import re

stop_words = set(stopwords.words('english'))
vocabulary = words.words()
N = len(vocabulary)
# vocabulary = {i:vocabulary.index(i) for i in vocabulary}


def small_case(text):
    """
    Converts text to lowercase and removes punctuation and digits and special characters.
    :param text: Text to be converted to lowercase
    :return: converted Text
    """
    text = text.lower()
    text = re.sub('[^a-z]+', ' ', text)

    return text.strip()


def one_hot_encode(text, stop_words_list, vocabulary_list):
    """
    Converts text to one-hot vector and removes punctuation and digits and special characters.
    :param text: Text to be converted to one-hot vector
    :param stop_words_list: list of stop words
    :param vocabulary_list: list of all words in vocabulary vector
    :return: converted one-hot vector
    """

    text = small_case(text)
    text = text.split(" ")
    text = [i for i in text if i not in stop_words_list]

    N = len(vocabulary_list)

    one_hot = np.zeros(N, dtype='int')

    for word in text:
        if word in vocabulary_list:
            one_hot[vocabulary_list.index(word)] = 1

    return one_hot


def cosine_similarity(vec1, vec2):
    """
    Calculates the cosine similarity between two vectors.
    :param vec1: First vector
    :param vec2: Second vector
    :return: cosine similarity between two vectors
    """

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


if __name__ == '__main__':
    doc1 = """
    I love to eat apples and bananas.
    """

    doc2 = """
    I like to eat bananas.
    """

    doc3 = """
    Do you prefer reading?
    """

    # create vectors from documents
    doc1 = one_hot_encode(doc1, stop_words, vocabulary)
    doc2 = one_hot_encode(doc2, stop_words, vocabulary)
    doc3 = one_hot_encode(doc3, stop_words, vocabulary)

    # compare vectors
    print("Similarity between Doc1 and Doc2:",cosine_similarity(doc1, doc2))
    print("Similarity between Doc1 and Doc3:",cosine_similarity(doc1, doc3))
    print("Similarity between Doc2 and Doc3:",cosine_similarity(doc2, doc3))

