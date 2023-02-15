from .alignments_new import check_word_compounding
from .alignments import get_alignment_words, get_alignment_chars, print_alignment_words
from .distances import distance
import Levenshtein
from collections import defaultdict

import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from . import compound_data

'''

Things to return:
WER
CER
Word miss pairs
Character miss pairs
Compounds created
Compounds deleted
Known compounds

'''

def compute_mistakes(reference, hypothesis, utterance_ids=[], known_compounds=set(), distance_method='Levenshtein', print_to_file='', allow_greater_than_1_sub_cost=False, compute_cer_with_weighted_alignment=False, language='no') -> dict:
    """
    :param reference: the ground-truth sentence(s) as a string or list of strings
    :param hypothesis: the hypothesis sentence(s) as a string or list of strings
    :param utterance_ids: a list of IDs that correspond to each reference-hypothesis pair
    :param known_compounds: a set of known compound words to look for in the reference sentences
    :param distance_method: how should the alignment between the reference be generated. Valid options are: 'Levenshtein', 'unweighted_manual', 'weighted_manual'
    :param print_to_file: file to print resulting alignments to. If left empty no alignment file is generated
    :param allow_greater_than_1_sub_cost: used when computing manual weighted alignment. Will allow the substitutions cost to be greater than 1
    :return: a dict with results. for full details on return dictionary elements please see the readme file
    """
    # first calculate the distance and backtrace for the utterances
    accepted_distance_methods = ['Levenshtein', 'unweighted_manual', 'weighted_manual']
    if distance_method not in accepted_distance_methods:
        raise Exception('Unknown distance method: {}. Please select one of {}'.format(distance_method, ', '.join(accepted_distance_methods)))

    if len(known_compounds) == 0:
        known_compounds = _read_compound_list()
    
    # put strings in a list so they'll safely work for the following for loop
    if isinstance(reference, str):
        reference = [reference]
    if isinstance(hypothesis, str):
        hypothesis = [hypothesis]
    if isinstance(utterance_ids, str):
        utterance_ids = [utterance_ids]
    if len(utterance_ids) < len(reference):
        utterance_ids = utterance_ids + ['UNK_ID'] * (len(reference) -  len(utterance_ids))

    # declare variables we want to track across loops
    word_level_errors = 0
    word_level_references = 0
    char_level_error = 0
    char_level_references = 0
    compounds_created = 0
    compounds_deleted = 0
    joins_in_created_compound = 0
    joins_in_broken_compound = 0
    word_miss_pairs = defaultdict(int)
    compound_miss_pairs = defaultdict(int)
    char_miss_pairs_word_bound = defaultdict(int)
    char_miss_trigrams_word_bound = defaultdict(int)
    char_miss_pairs_word_unbound = defaultdict(int)
    known_compounds_achieved = defaultdict(int)
    known_coupounds_missed = defaultdict(int)
    final_print = ''

    for (ref, hyp, utt_id) in zip(reference, hypothesis, utterance_ids):
        # ### FOR DEBUGGING
        # print(ref)
        dist = distance(ref, hyp, language)
        computed_editops = []
        if distance_method == 'Levenshtein':
            computed_editops = dist.get_levenshtein_editops()
        elif distance_method == 'unweighted_manual':
            computed_editops = dist.get_unweighted_editops()
        else:
            computed_editops = dist.get_weighted_editops(allow_greater_than_1=allow_greater_than_1_sub_cost)

        # now take the edit operations and adjust the utterances to they align (e.g. add spaces where there was an insertion or deletion)
        changes_tuples, index_changes, ref, hyp = get_alignment_words(ref, hyp, computed_editops)
        # now check if we have any compound words that have been created or deleted
        ref, hyp, changes_tuples, index_changes, created_compound, brokeup_compound, join_in_created_compound, join_in_broken_compound = check_word_compounding(ref, hyp, changes_tuples)

        word_align = print_alignment_words(ref, hyp, language, index_changes=index_changes, only_print_subs=False, do_print=False)

        edit_count_word = len(changes_tuples)
        ref_count_word = len(ref)
        if compute_cer_with_weighted_alignment:
            char_editops = distance(' '.join(ref), ' '.join(hyp), language).get_weighted_character_editops()
        else:
            char_editops = Levenshtein.editops(' '.join(ref), ' '.join(hyp))
        changes_tuples_chars, index_changes_chars, ref_char, hyp_char = get_alignment_chars(' '.join(ref), ' '.join(hyp), char_editops)
        edit_count_char = len(char_editops)
        ref_count_char = len(' '.join(ref))

        # add to cross-loop tracking
        word_level_errors += edit_count_word
        word_level_references += ref_count_word
        char_level_error += edit_count_char
        char_level_references += ref_count_char
        compounds_created += created_compound
        compounds_deleted += brokeup_compound
        joins_in_created_compound += join_in_created_compound
        joins_in_broken_compound += join_in_broken_compound

        word_miss_pairs, compound_miss_pairs, char_miss_pairs_word_bound, char_miss_trigrams_word_bound = _count_word_mistakes(index_changes, ref, hyp, language, word_miss_pairs, compound_miss_pairs, char_miss_pairs_word_bound, char_miss_trigrams_word_bound)

        for change_tup in changes_tuples_chars:
            add_tuple = str((change_tup[0], change_tup[1]))
            char_miss_pairs_word_unbound[add_tuple] += 1

        # check for known compounds in the reference
        for word_i in range(len(ref)):
            ref_word = ref[word_i]
            if ref_word in known_compounds:
                if word_i in index_changes:
                    known_coupounds_missed[ref_word] += 1
                else:
                    known_compounds_achieved[ref_word] += 1

        final_print += '--- {} (WER: {}, compounds created: {}, compounds broken up: {})---\n'.format(
            utt_id, 
            round(100 * (edit_count_word / ref_count_word), 2), 
            created_compound, 
            brokeup_compound
        ) + "\n".join(word_align) + "\n\n"

    if print_to_file:
        with open(print_to_file, 'w') as f_open:
            f_open.write(final_print)

    return {
        'word_level_errors' : word_level_errors,
        'word_level_references' : word_level_references,
        'char_level_errors' : char_level_error,
        'char_level_references' : char_level_references,
        'compounds_created' : compounds_created,
        'compounds_deleted' : compounds_deleted,
        'joins_in_created_compound' : joins_in_created_compound,
        'joins_in_broken_compound' : joins_in_broken_compound,
        'word_miss_pairs' : word_miss_pairs,
        'compound_miss_pairs' : compound_miss_pairs,
        'char_miss_pairs_word_bound' : char_miss_pairs_word_bound,
        'char_miss_pairs_word_unbound' : char_miss_pairs_word_unbound,
        'char_miss_trigrams_word_bound' : char_miss_trigrams_word_bound,
        'known_compounds_achieved' : known_compounds_achieved,
        'known_coupounds_missed' : known_coupounds_missed,
        'final_print' : final_print
    }

def wer(results: dict, level_of_precision=3) -> float:
    '''
    :param results: the results object returned from compute_mistakes()
    :return: WER
    '''
    if not results['word_level_references']:
        return None
    return round(100 * (results['word_level_errors']/results['word_level_references']), level_of_precision)

def cer(results: dict, level_of_precision=3) -> float:
    '''
    :param results: the results object returned from compute_mistakes()
    :return: CER
    '''
    return round(100 * (results['char_level_errors']/results['char_level_references']), level_of_precision)

def cer_word_aligned(results: dict, level_of_precision=3) -> float:
    '''
    :param results: the results object returned from compute_mistakes()
    :return: CER (as computed after word-level alignment)
    '''
    char_error_counts = sum(results['char_miss_pairs_word_bound'].values())
    return round(100 * (char_error_counts/results['char_level_references']), level_of_precision)

def _read_compound_list() -> set:
    compound_list = pkg_resources.read_text(compound_data, 'compound_word_list.txt')
    compound_list = set([w.strip().lower() for w in compound_list.split('\n')])
    return(compound_list)

def _get_word_level_character_changes(ref_word, hyp_word, language):
    ref_word = ref_word if ref_word != ' ' else ''
    hyp_word = hyp_word if hyp_word != ' ' else ''
    word_char_changes_tuples, word_char_index_changes, word_char_ref, word_char_hyp = get_alignment_chars(
            ref_word, 
            hyp_word, 
            # Levenshtein.editops(ref_word, hyp_word)
            distance(ref_word, hyp_word, language).get_weighted_character_editops()
        )
    return word_char_changes_tuples

def _get_word_level_character_change_trigrams(ref_word, hyp_word, language):
    ref_word = ref_word if ref_word != ' ' else ''
    hyp_word = hyp_word if hyp_word != ' ' else ''
    word_char_changes_tuples, word_char_index_changes, word_char_ref, word_char_hyp = get_alignment_chars(
            ref_word, 
            hyp_word, 
            # Levenshtein.editops(ref_word, hyp_word)
            distance(ref_word, hyp_word, language).get_weighted_character_editops()
        )
    change_trigrams = []
    for index_change in word_char_index_changes.keys():
        change_trigrams.append(
            (
                ''.join((
                    word_char_ref[index_change-1] if index_change-1 > -1 else '_', 
                    word_char_ref[index_change],
                    word_char_ref[index_change+1] if index_change+1 < len(word_char_ref) else '_'
                )),
                ''.join((
                    word_char_hyp[index_change-1] if index_change-1 > -1 else '_', 
                    word_char_hyp[index_change],
                    word_char_hyp[index_change+1] if index_change+1 < len(word_char_hyp) else '_'
                ))
            )
        )
    return change_trigrams

def _count_word_character_mistakes(word_char_changes_tuples, char_miss_pairs_word_bound):
    for word_char_change_tup in word_char_changes_tuples:
        add_tuple = str((word_char_change_tup[0], word_char_change_tup[1]))
        char_miss_pairs_word_bound[add_tuple] += 1
    return char_miss_pairs_word_bound

def _count_word_mistakes(index_changes, ref, hyp, language, word_miss_pairs, compound_miss_pairs, char_miss_pairs_word_bound, char_miss_trigrams_word_bound):
    for index_change in index_changes:
        ref_token = ref[index_change]
        hyp_token = hyp[index_change]
        if ref_token == ' ' or hyp_token == ' ':
            # this is a word-level insertion or deletion
            word_miss_pairs[str((ref_token, hyp_token))] += 1
        else:
            if ' ' in ref_token or ' ' in hyp_token:
                compound_miss_pairs[str((ref_token, hyp_token))] += 1
            else:
                word_miss_pairs[str((ref_token, hyp_token))] += 1
        # now add in the inter-word character changes
        char_miss_pairs_word_bound = _count_word_character_mistakes(_get_word_level_character_changes(ref_token, hyp_token, language), char_miss_pairs_word_bound)
        char_miss_trigrams_word_bound = _count_word_character_mistakes(_get_word_level_character_change_trigrams(ref_token, hyp_token, language), char_miss_trigrams_word_bound)

    return word_miss_pairs, compound_miss_pairs, char_miss_pairs_word_bound, char_miss_trigrams_word_bound

        