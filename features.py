from __future__ import division
from statistics import pvariance
from re import findall

# returns (number of sentences with at least one relative clause) / (total number of sentences)
def relative_clause_sentence_frequency(text):
    sentences = _get_sentences(text)
    return len(filter(_get_relative_clauses, sentences)) / len(sentences)

# returns (number of relative clauses) / (number of sentences)
def relative_clauses_per_sentence_average(text):
    sentences = _get_sentences(text)
    return len(sum(map(_get_relative_clauses, sentences), [])) / len(sentences)

# returns the average length of a relative clause, in words
def relative_clause_length_average(text):
    sentences = _get_sentences(text)
    all_clauses = sum(map(_get_relative_clauses, sentences), [])
    return len(map(lambda clause: len(clause.split(' ')), all_clauses)) / len(all_clauses) if all_clauses else 0

# average sentence length, measured in alphabetic characters
def sentence_length_average(text):
    sentences = _get_sentences(text)
    return sum(map(_alphabetic_char_count, sentences)) / len(sentences)

# variance of sentence lengths in alphabetic characters
def sentence_length_variance(text):
    return pvariance(map(_alphabetic_char_count, _get_sentences(text)))

# ratio of superlative adjective count / total word count
def superlative_adjective_frequency(text):
    words = _get_words(text)
    return len([word for word in words if 'issim' in word]) / len(words)

# ratio of interrogative clause count / total sentence count
def interrogative_sentence_frequency(text):
    sentences = _get_sentences(text)
    return len(filter(lambda sentence: '?' in sentence, sentences)) / len(sentences)

# ratio of conjunction count / total word count
def conjunction_frequency(text):
    words = _get_words(text)
    return len(filter(_is_conjunction, words)) / len(words)

# ratio of gerund count / total word count
def gerund_frequency(text):
    words = _get_words(text)
    return len(filter(_is_gerund, words)) / len(words)

# number of occurences of the word 'alius' / total number of words
def alius_frequency(text):
    words = _get_words(text)
    return len(filter(lambda word: word.lower() == 'alius', words)) / len(words)

# This is based on the `freqOfNeque` and `freqOfNequeNeq` functions in the original featureextractor,
# except that it normalizes for the total number of sentences. It appears to compute the ratio of sentences
# containing the word `neque` twice and sentences that contain both 'neque' and 'aut'. However,
# QUESTION: I'm not sure I understand the significance of this metric, so we should verify that it's
# being calculated correctly.
def neque_aut_ratio(text):
    def has_neque_and_aut(sentence):
        words = set(map(lambda word: word.rstrip('.,?'), sentence.lower().split(' ')))
        return 'neque' in words and 'aut' in words

    sentences = _get_sentences(text)
    return _safe_ratio(len(filter(_has_neque_twice, sentences)), len(filter(has_neque_and_aut, sentences)))

# This is based on the `freqOfNequeNec` function in the original featureextractor, except
# that it normalizes for the total number of sentences. It computes the ratio of sentences
# containing the word `neque` twice and sentences that contain the word `neq`.
# QUESTION: I'm not sure I understand the significance of this metric, so we should verify that it's
# being calculated correctly.
def neque_nec_ratio(text):
    def has_nec(sentence):
        return 'nec' in map(lambda word: word.rstrip('.,?'), sentence.lower().split(' '))

    sentences = _get_sentences(text)
    return _safe_ratio(len(filter(_has_neque_twice, sentences)), len(filter(has_nec, sentences)))

# This is based on the `freqVocative` function in the original featureextractor, except that it
# normalizes for the total number of words. It appears to compute the number of occurences of 'O'
# followed by a word ending in 'e' followed by a comma.
# QUESTION: I'm not sure I understand the significance of this metric, so we should verify that it's
# being calculated correctly.
def vocative_frequency(text):
    words = _get_words(text)
    return len([word for index,word in enumerate(words[:-1]) if word == 'O' and len(words[index + 1]) > 2 and words[index + 1][-2:] == 'e,']) / len(words)

# Returns the ratio of (occurences of 'atque' followed by a consonant) / (total number of words)
def atque_consonant_frequency(text):
    words = _get_words(text)
    # QUESTION: This is the list of consonants from the original `freqAtqueCons` function, but
    # aren't there more than 5 consonants in total? Or does this metric only apply to specific consonants?
    VOWELS = {'a', 'e', 'i', 'o', 'u'}
    return len([word for index,word in enumerate(words[:-1]) if word.lower() == 'atque' and words[index + 1] and words[index + 1][0] not in VOWELS]) / len(words)

# Returns the ratio of
# (occurences of the conjunction 'cum' that are not followed by a word ending in 'a', 'e', 'is', 'ibus', 'ebus') / total number of words
# QUESTION: I'm not sure I understand the significance of this metric, so we should verify that it's
# being calculated correctly.
def conjunction_cum_frequency(text):
    suffixes = {'a', 'e', 'is', 'ibus', 'ebus', 'o', 'u', 'ubus'}
    def has_suffix(word):
        return any(map(lambda suffix: word.endswith(suffix), suffixes))
    words = _get_words(text)
    return len([word for index,word in enumerate(words[:-1]) if word.lower() == 'cum' and words[index + 1] and not has_suffix(words[index + 1])]) / len(words)

def _words_frequency(words):
    word_set = set(words)
    def frequency(text):
        text_words = _get_words(text.lower())
        return len(filter(lambda word: word in word_set, text_words)) / len(text_words)
    return frequency

_word_frequency = lambda word: _words_frequency({word})

cond_cl_frequency = _words_frequency({'si', 'nisi', 'quodsi'})
third_person_pronoun_frequency = _words_frequency({'se', 'sibi', 'sese', 'sui'})
demonstrative_pronoun_frequency = _words_frequency({
    "hic", "hunc", "huius", "huic", "hoc", "hec", "hanc", "hac", "hi", "hos", "horum", "his",
    "hiis", "has", "harum", "ille", "illum", "illius",
    "illi", "illo", "illa", "illam", "illud", "illos", "illorum",
    "illis", "illas", "illarum", "is", "eum", "eius", "ei", "eo", "ea",
    "eam", "id", "ii", "eos", "eorum", "eis", "iis", "eae",
    "ee", "eas", "earum"
})

personal_pronoun_frequency = _words_frequency({
    "ego", "mei", "mihi", "me", "tu", "tui", "tibi", "te", "is",
    "eius", "ei", "eum", "eo",
    "ea", "eam", "id", "nos", "nostri", "nobis", "vos",
    "vestri", "vobis", "eorum", "eis", "eos", "eae", "earum",
    "eas"
})

ipse_ngram_frequency = _words_frequency({
    "ipse", "ipsum","ipsius", "ipsi", "ipso", "ipsa",
    "ipsam", "ipsos", "ipsorum", "ipsas", "ipsarum"
})

idem_ngram_frequency = _words_frequency({
    "idem", "eundem", "eiusdem", "eidem", "eodem",
    "eadem", "eandem", "iidem", "eosdem", "eorundem",
    "eisdem", "iisdem", "eaedem", "eedem", "easdem", "earumdem"
})

indef_frequency = _words_frequency({
    "quidam", "quendam", "cuiusdam", "cuidam", "quodam",
    "quedam", "quandam", "quodam", "quoddam", "quosdam",
    "quorundam", "quibusdam", "quasdam", "quarundam"
})

iste_ngram_frequency = _words_frequency({"iste", "istum", "istius", "isti", "isto", "ista", "istam", "istud", "istos", "istorum", "istis", "istas", "istarum"})

ut_frequency = _words_frequency({"ut"})

quominus_frequency = _words_frequency({"quominus"})

dum_frequency = _words_frequency({"dum"})

priusquam_frequency = _words_frequency({"priusquam"})

antequam_frequency = _words_frequency({"antequam"})

quin_frequency = _words_frequency({"quin"})





# number of alphabetic characters
def _alphabetic_char_count(text):
    return len(filter(lambda char: char.isalpha(), text))

#Gets a list of sentences given a string representing text.
def _get_sentences(text):
	sentences = []
	current_sentence = ''
	for char in text:
		current_sentence += char
		# Last condition in the if doesn't let a sentence end with a one (capital) letter word and then a period.
		# This is to prevent against abbrev first names in Livy splitting sentences
		if (char in {'.', '?', '!'} and len(current_sentence) >= 3
			and current_sentence[-3].isalpha()
			and not (
                current_sentence[-3] == ' '
                and current_sentence[-2].upper() == current_sentence[-2]
                and current_sentence[-1] == '.'
            )
        ):
			sentences.append(current_sentence)
			current_sentence = ''

	if current_sentence:
		sentences.append(current_sentence)

	return sentences

def _get_words(text):
    return filter(lambda word: word, sum([sentence.split(' ') for sentence in _get_sentences(text)], []))

def _get_relative_clauses(sentence):
    RELATIVE_PRONOUNS = ['qui', 'cuius', 'cui', 'quem', 'quo', 'quae', 'quam', 'qua', 'quod', 'quorum', 'quibus', 'quos', 'quarum', 'quas']
    if sentence[-1] == '?':
        return []
    return findall('(?:' + '|'.join(RELATIVE_PRONOUNS) + ')[\\w ]*', sentence)

def _safe_ratio(value1, value2):
    return value1 / value2 if value2 else 99 if value1 else 0

def _is_conjunction(word):
    CONJUNCTIONS = {'atque', 'ac', 'neque', 'aut', 'vel', 'at', 'autem', 'sed', 'tamen', 'postquam', 'uel'}
    return word in CONJUNCTIONS or word[-3:] == 'que'

def _is_gerund(word):
    return word[-4:] == 'ndum' or word[-4:] == 'nuds'

def _has_neque_twice(sentence):
    return map(lambda word: word.rstrip('.,?'), sentence.lower().split(' ')).count('neque') == 2
