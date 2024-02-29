import Levenshtein
import pandas as pd
import numpy as np
from copy import deepcopy
from operator import itemgetter
from itertools import chain

from .distances import distance

# ignore_chars = ['è', 'é', 'ò', 'ö', 'ü']

def string_insert(string, index, insert_me):
    return string[:index] + insert_me + string[index:]

def get_alignment_chars(ref, hyp, ops):

    ref_index_adjustment = 0
    hyp_index_adjustment = 0
    index_changes = {}
    changes_tuples = []

    for op in ops:
        if op[0] == 'insert':
            # incrementing this here to deal with exlusive ranges
            ref_index_adjustment += 1
            tracking_index = op[2] + hyp_index_adjustment
            # ref.insert(tracking_index, ' ')
            ref = string_insert(ref, tracking_index, ' ')
            index_changes[tracking_index] = 'I'
            hyp_insert = hyp[tracking_index]
            # 20230215 I have no rememberance of why ignore_chars is here so we're going to get rid of it
            # if hyp_insert not in ignore_chars and hyp_insert != ' ':
            if hyp_insert != ' ':
                changes_tuples.append((' ', hyp_insert, tracking_index))
            
        elif op[0] == 'delete':
            # incrementing this here to deal with exlusive ranges
            hyp_index_adjustment += 1
            tracking_index = op[1] + ref_index_adjustment
            # hyp.insert(tracking_index, ' ')
            hyp = string_insert(hyp, tracking_index, ' ')
            index_changes[tracking_index] = 'D'
            ref_del = ref[tracking_index]
            # 20230215 I have no rememberance of why ignore_chars is here so we're going to get rid of it
            # if ref_del not in ignore_chars and ref_del != ' ':
            if ref_del != ' ':
                changes_tuples.append((ref_del, ' ', tracking_index))
        else:
            ### debugging 
            if op[1] + ref_index_adjustment != op[2] + hyp_index_adjustment:
                raise Exception('ref and hyp are somehow different lengths!')
            tracking_index = op[1] + ref_index_adjustment
            ### ### ### 
            index_changes[tracking_index] = 'S'
            changes_tuples.append((ref[tracking_index], hyp[tracking_index], tracking_index))
    return changes_tuples, index_changes, ref, hyp

def get_alignment_words(ref, hyp, ops):
    ref_index_adjustment = 0
    hyp_index_adjustment = 0
    index_changes = {}
    changes_tuples = []

    ref = deepcopy(ref)
    hyp = deepcopy(hyp)

    # split on spaces (if they're not already split)
    if isinstance(ref, str):
        ref = ref.split(' ')
    if isinstance(hyp, str):
        hyp = hyp.split(' ')

    for op in ops:
        if op[0] == 'insert':
            # incrementing this here to deal with exlusive ranges
            ref_index_adjustment += 1
            tracking_index = op[2] + hyp_index_adjustment
            ref.insert(tracking_index, ' ')
            index_changes[tracking_index] = ' '
            hyp_insert = hyp[tracking_index]
            # 20230215 I have no rememberance of why ignore_chars is here so we're going to get rid of it
            # if hyp_insert not in ignore_chars and hyp_insert != ' ':
            if hyp_insert != ' ':
                changes_tuples.append((' ', hyp_insert, tracking_index))
            
        elif op[0] == 'delete':
            # incrementing this here to deal with exlusive ranges
            hyp_index_adjustment += 1
            tracking_index = op[1] + ref_index_adjustment
            hyp.insert(tracking_index, ' ')
            index_changes[tracking_index] = ' '
            ref_del = ref[tracking_index]
            # 20230215 I have no rememberance of why ignore_chars is here so we're going to get rid of it
            # if ref_del not in ignore_chars and ref_del != ' ':
            if ref_del != ' ':
                changes_tuples.append((ref_del, ' ', tracking_index))
        else:
            ### debugging 
            if op[1] + ref_index_adjustment != op[2] + hyp_index_adjustment:
                raise Exception('ref and hyp are somehow different lengths!')
            tracking_index = op[1] + ref_index_adjustment
            ### ### ### 
            index_changes[tracking_index] = 'S'
            changes_tuples.append((ref[tracking_index], hyp[tracking_index], tracking_index))
    return changes_tuples, index_changes, ref, hyp


def print_alignment_chars(ref, hyp, ops, do_print=True, max_width=250, only_print_subs=False):
    changes_tuples, index_changes, ref, hyp = get_alignment_chars(ref, hyp, ops)
    ref_print_str = ''
    hyp_print_str = ''
    chg_print_str = ''
    for i in range(len(ref)):
        ref_print_str += ' {} |'.format(ref[i])
        hyp_print_str += ' {} |'.format(hyp[i])
        if i in index_changes:
            if only_print_subs:
                if index_changes[i] == 'S':
                    chg_print_str += ' {} |'.format(index_changes[i])
                else:
                    chg_print_str += ' {} |'.format(' ')
            else:
                chg_print_str += ' {} |'.format(index_changes[i])
        else:
            chg_print_str += '   |'
    if do_print:
        if len(ref_print_str) > max_width:
            start_index = 0
            end_index = max_width
            while start_index < len(ref_print_str) - 1:
                print(ref_print_str[start_index:end_index])
                print(hyp_print_str[start_index:end_index])
                print(chg_print_str[start_index:end_index])
                print()
                start_index = end_index
                end_index = end_index + max_width if end_index + max_width < len(ref_print_str) else len(ref_print_str) - 1
        else:
            print(ref_print_str)
            print(hyp_print_str)
            print(chg_print_str)
            print()
    return ref_print_str, hyp_print_str, chg_print_str

def print_alignment_words(ref, hyp, char_dists, index_changes={}, do_print=False, print_char_alignments=True, only_print_subs=False, max_width=250):
    ref = deepcopy(ref)
    hyp = deepcopy(hyp)

    # split on spaces (if they're not already split)
    if isinstance(ref, str):
        ref = ref.split(' ')
    if isinstance(hyp, str):
        hyp = hyp.split(' ')

    # check if we need to do alignment
    if not index_changes:
        # tokenize each word into an integer
        vocabulary = list(set(chain(ref, hyp)))

        word2char = {vocabulary[vocab_number]: chr(vocab_number) for vocab_number in range(len(vocabulary))}

        truth_chars = "".join([word2char[w] for w in ref])
        hypothesis_chars = "".join([word2char[w] for w in hyp])

        editops = Levenshtein.editops(truth_chars, hypothesis_chars)

        changes_tuples, index_changes, ref, hyp = get_alignment_words(ref, hyp, editops)
    
    ref_print_str = ''
    hyp_print_str = ''
    chg_print_str = ''

    def pad_alignment_token(tok, target_len):
        need_to_add_total = target_len - len(tok)
        add_each_side = int(need_to_add_total/2)
        return ' ' * add_each_side + tok + ' ' * (add_each_side if need_to_add_total%2 == 0 else add_each_side + 1)

    for i in range(len(ref)):
        longest_alignment_token = max(len(ref[i]), len(hyp[i]))
        if print_char_alignments:
            if i in index_changes:
                if only_print_subs:
                    use_ref = ref[i] if ref[i] != ' ' else ''
                    use_hyp = hyp[i] if hyp[i] != ' ' else ''
                    char_ref_str, char_hyp_str, char_cng_str = print_alignment_chars(
                        use_ref, 
                        use_hyp, 
                        # Levenshtein.editops(
                        #     ref[i] if ref[i] != ' ' else '', 
                        #     hyp[i] if hyp[i] != ' ' else ''
                        # ),
                        distance(use_ref, use_hyp, char_dists).get_weighted_character_editops(),
                        do_print=False, 
                        only_print_subs=True
                    )
                    # the char strings should all be the same length
                    if index_changes[i] == 'S':
                        longest_alignment_token = len(char_ref_str)
                        longest_alignment_token = len(char_ref_str)
                        chg_print_str += ' {}  || '.format(pad_alignment_token(char_cng_str.strip('|'), longest_alignment_token))
                        ref_print_str += ' {}  || '.format(pad_alignment_token(char_ref_str.strip('|'), longest_alignment_token))
                        hyp_print_str += ' {}  || '.format(pad_alignment_token(char_hyp_str.strip('|'), longest_alignment_token))
                    else:
                        chg_print_str += ' {}  || '.format(pad_alignment_token(' ', longest_alignment_token))
                        ref_print_str += ' {}  || '.format(pad_alignment_token(ref[i], longest_alignment_token))
                        hyp_print_str += ' {}  || '.format(pad_alignment_token(hyp[i], longest_alignment_token))
                else:
                    use_ref = ref[i] if ref[i] != ' ' else ''
                    use_hyp = hyp[i] if hyp[i] != ' ' else ''
                    char_ref_str, char_hyp_str, char_cng_str = print_alignment_chars(
                        use_ref, 
                        use_hyp, 
                        # Levenshtein.editops(
                        #     ref[i] if ref[i] != ' ' else '', 
                        #     hyp[i] if hyp[i] != ' ' else ''
                        # ),
                        distance(use_ref, use_hyp, char_dists).get_weighted_character_editops(),
                        do_print=False, 
                        only_print_subs=False
                    )
                    longest_alignment_token = len(char_ref_str)
                    chg_print_str += ' {}  || '.format(pad_alignment_token(char_cng_str.strip('|'), longest_alignment_token))
                    ref_print_str += ' {}  || '.format(pad_alignment_token(char_ref_str.strip('|'), longest_alignment_token))
                    hyp_print_str += ' {}  || '.format(pad_alignment_token(char_hyp_str.strip('|'), longest_alignment_token))
            else:
                chg_print_str += ' {}  || '.format(pad_alignment_token(' ', longest_alignment_token))
                ref_print_str += ' {}  || '.format(pad_alignment_token(ref[i], longest_alignment_token))
                hyp_print_str += ' {}  || '.format(pad_alignment_token(hyp[i], longest_alignment_token))
        else:
            if i in index_changes:
                if ref[i] == ' ':
                    chg_print_str += ' {}  || '.format(pad_alignment_token('I', longest_alignment_token))
                elif hyp[i] == ' ':
                    chg_print_str += ' {}  || '.format(pad_alignment_token('D', longest_alignment_token))
                else:
                    chg_print_str += ' {}  || '.format(pad_alignment_token(index_changes[i], longest_alignment_token))
            else:
                chg_print_str += ' {}  || '.format(pad_alignment_token(' ', longest_alignment_token))

            ref_print_str += ' {}  || '.format(pad_alignment_token(ref[i], longest_alignment_token))
            hyp_print_str += ' {}  || '.format(pad_alignment_token(hyp[i], longest_alignment_token))
    
    if do_print:
        if len(ref_print_str) > max_width:
            start_index = 0
            end_index = max_width
            while start_index < len(ref_print_str) - 1:
                print(ref_print_str[start_index:end_index])
                print(hyp_print_str[start_index:end_index])
                print(chg_print_str[start_index:end_index])
                print()
                start_index = end_index
                end_index = end_index + max_width if end_index + max_width < len(ref_print_str) else len(ref_print_str) - 1
        else:
            print(ref_print_str)
            print(hyp_print_str)
            print(chg_print_str)

    return(ref_print_str, hyp_print_str, chg_print_str)

def get_character_del_count(ref, hyp, char_dists):
    # return len([edtop for edtop in Levenshtein.editops(ref, hyp) if edtop[0] == 'delete'])
    return len([edtop for edtop in distance(ref, hyp, char_dists).get_weighted_character_editops() if edtop[0] == 'delete'])

def get_character_ins_count(ref, hyp, char_dists):
    # return len([edtop for edtop in Levenshtein.editops(ref, hyp) if edtop[0] == 'insert'])
    return len([edtop for edtop in distance(ref, hyp, char_dists).get_weighted_character_editops() if edtop[0] == 'insert'])

def get_character_change_count(ref, hyp, char_dists):
    # return len([edtop for edtop in Levenshtein.editops(ref, hyp)])
    return len([edtop for edtop in distance(ref, hyp, char_dists).get_weighted_character_editops()])

def check_word_compounding(changes_tuples, index_changes, ref, hyp, char_dists):
    created_compound=0
    brokeup_compound=0
    i = 0
    while i < len(changes_tuples):
        change_tup = changes_tuples[i]
        change_index = change_tup[2]
        # initalize all the valuse as nan to make later comparisons w/ 0 easy
        left_delta_ins, right_delta_ins, \
        left_delta_del, right_delta_del, \
        left_delta_edit, right_delta_edit, \
        left_base_ins_count, left_compound_ins_count, \
        left_base_del_count, left_compound_del_count, \
        right_base_ins_count, right_compound_ins_count, \
        right_base_del_count, right_compound_del_count, \
        left_base_edit_count, left_compound_edit_count, \
        right_base_edit_count, right_compound_edit_count = tuple([np.nan]) * 18

        if change_tup[0] == ' ':
            # this is the case where the referece has a compound word and the compound might have been broken up
            # ||  han  ||     |   |      ||  h | e | r | f | r | a  ||
            # ||  han  ||   h | e | r    ||    |   |   | f | r | a  ||
            # ||       ||     |   |      ||  D | D | D |   |   |    ||
            if change_index - 1 >= 0 and hyp[change_index-1] not in ['', ' ']:
                # left_base_cer = get_character_error_rate(ref[change_index-1], hyp[change_index-1])
                left_base_del_count = get_character_del_count(ref[change_index-1], hyp[change_index-1], char_dists)
                # left_compound_cer = get_character_error_rate(ref[change_index-1], hyp[change_index-1] + change_tup[0])
                left_compound_del_count = get_character_del_count(ref[change_index-1], hyp[change_index-1] + change_tup[1], char_dists)

                left_base_edit_count = get_character_change_count(ref[change_index-1], hyp[change_index-1])
                left_compound_edit_count = get_character_change_count(ref[change_index-1], hyp[change_index-1] + change_tup[1], char_dists)

            if change_index + 1 < len(ref) and hyp[change_index+1] not in ['', ' ']:
                # right_base_cer = get_character_error_rate(ref[change_index+1], hyp[change_index+1])
                right_base_del_count = get_character_del_count(ref[change_index+1], hyp[change_index+1], char_dists)
                # right_compound_cer = get_character_error_rate(ref[change_index+1], change_tup[1] + hyp[change_index+1])
                right_compound_del_count = get_character_del_count(ref[change_index+1], change_tup[1] + hyp[change_index+1], char_dists)

                right_base_edit_count = get_character_change_count(ref[change_index+1], hyp[change_index+1], char_dists)
                right_compound_edit_count = get_character_change_count(ref[change_index+1], change_tup[1] + hyp[change_index+1], char_dists)

            # left_delta = left_base_cer - left_compound_cer 
            left_delta_del = left_base_del_count - left_compound_del_count
            # right_delta = right_base_cer - right_compound_cer
            right_delta_del= right_base_del_count - right_compound_del_count

            left_delta_edit = left_base_edit_count - left_compound_edit_count
            right_delta_edit = right_base_edit_count - right_compound_edit_count
            
            # if a delta is positive then the CER improved, if it's negative the CER got worse
            if left_delta_del  > 0 and right_delta_del  > 0:
                # not 100% sure this is the correct way of choosing but we'll just choose whichever has had the biggest improvement
                if left_delta_del  > right_delta_del :
                    # the logic below will evaluate left first so we don't need to make any changes
                    pass
                else:
                    # set left_delta to 0 so the following if statement fails and it goes to the elif
                    left_delta_del = 0
            
            if left_delta_del  > 0 and left_delta_edit > 0:
                brokeup_compound += 1
                # adjust the hypothesis to have the compound but keep a space so the character comparison will realize the change 
                hyp[change_index-1] = hyp[change_index-1] + ' ' + change_tup[1]
                # remove the extra word and deletion space
                popped_ref = ref.pop(change_index)
                popped_hyp = hyp.pop(change_index)
                # remove the change from the index changes
                # update the change indexs...
                # since we've removed a word we'll need to decrease all indexs >= current index by 1
                # but first remove the change we've been working with 
                popped_index = index_changes.pop(change_index)
                # now decrease indexes 
                index_changes = {(k-1 if k > change_index else k): v for k, v in index_changes.items()}
                # adjust the changes_tuples list
                popped_change_tup = changes_tuples.pop(i)
                # update the indexes in change tuples as well now
                changes_tuples = [((ct[0], ct[1], ct[2]-1) if ct[2] > change_index else ct) for ct in changes_tuples]
                # don't increment i because we've decreased the changes_tuple list so i should now be pointing at the next item
            elif right_delta_del  > 0 and right_delta_edit > 0:
                brokeup_compound += 1
                # adjust the reference to have the "compound" but keep a space so the character comparison will realize the change 
                hyp[change_index+1] = change_tup[1] + ' ' + hyp[change_index+1]
                # remove the extra word and deletion space
                popped_ref = ref.pop(change_index)
                popped_hyp = hyp.pop(change_index)
                # update the change indexs...
                # since we've removed a word we'll need to decrease all indexs >= current index by 1
                # but first remove the change we've been working with 
                popped_index = index_changes.pop(change_index)
                # now decrease indexes 
                index_changes = {(k-1 if k > change_index else k): v for k, v in index_changes.items()}
                # adjust the changes_tuples list
                popped_change_tup = changes_tuples.pop(i)
                # update the indexes in change tuples as well now
                changes_tuples = [((ct[0], ct[1], ct[2]-1) if ct[2] > change_index else ct) for ct in changes_tuples]
                # don't increment i because we've decreased the changes_tuple list so i should now be pointing at the next item
            else:
                # attempting to attach word to either neighborning word has made things worse...ergo we'll not do anything
                i += 1

        elif change_tup[1] == ' ':
            # this is the case where the reference has 2 words and a compound might have been made
            # ||  var  ||  offside  ||     |   |   |   |   |   | p | l | a | s | s | e | r | t    ||
            # ||  var  ||           ||   o | f | f | s | i | d | p | l | a | s | s | e | r | t    ||
            # ||       ||           ||   I | I | I | I | I | I |   |   |   |   |   |   |   |      ||
            if change_index - 1 >= 0 and ref[change_index-1] not in ['', ' ']:
                # left_base_cer = get_character_error_rate(ref[change_index-1], hyp[change_index-1])
                left_base_ins_count = get_character_ins_count(ref[change_index-1], hyp[change_index-1], char_dists)
                #  left_compound_cer = get_character_error_rate(ref[change_index-1] + change_tup[0], hyp[change_index-1])
                left_compound_ins_count = get_character_ins_count(ref[change_index-1] + change_tup[0], hyp[change_index-1], char_dists)

                left_base_edit_count = get_character_change_count(ref[change_index-1], hyp[change_index-1], char_dists)
                left_compound_edit_count = get_character_change_count(ref[change_index-1] + change_tup[0], hyp[change_index-1], char_dists)

            if change_index + 1 < len(ref) and ref[change_index+1] not in ['', ' ']:
                #  right_base_cer = get_character_error_rate(ref[change_index+1], hyp[change_index+1])
                right_base_ins_count = get_character_ins_count(ref[change_index+1], hyp[change_index+1], char_dists)
                #  right_compound_cer = get_character_error_rate(change_tup[0] + ref[change_index+1], hyp[change_index+1])
                right_compound_ins_count = get_character_ins_count(change_tup[0] + ref[change_index+1], hyp[change_index+1], char_dists)

                right_base_edit_count = get_character_change_count(ref[change_index+1], hyp[change_index+1], char_dists)
                right_compound_edit_count = get_character_change_count(change_tup[0] + ref[change_index+1], hyp[change_index+1], char_dists)
        
            #  left_delta = left_base_cer - left_compound_cer
            left_delta_ins = left_base_ins_count - left_compound_ins_count
            #  right_delta = right_base_cer - right_compound_cer
            right_delta_ins = right_base_ins_count - right_compound_ins_count
            
            left_delta_edit = left_base_edit_count - left_compound_edit_count
            right_delta_edit = right_base_edit_count - right_compound_edit_count

            # if a delta is positive then the CER improved, if it's negative the CER got worse
            if left_delta_ins > 0 and right_delta_ins > 0:
                # not 100% sure this is the correct way of choosing but we'll just choose whichever has had the biggest improvement
                if left_delta_ins > right_delta_ins:
                    # the logic below will evaluate left first so we don't need to make any changes
                    pass
                else:
                    # set left_delta to 0 so the following if statement fails and it goes to the elif
                    left_delta = 0
            
            if left_delta_ins > 0 and left_delta_edit > 0:
                created_compound += 1
                # adjust the reference to have the "compound" but keep a space so the character comparison will realize the change 
                ref[change_index-1] = ref[change_index-1] + ' ' + change_tup[0]
                # remove the extra word and deletion space
                popped_ref = ref.pop(change_index)
                popped_hyp = hyp.pop(change_index)
                # update the change indexs...
                # since we've removed a word we'll need to decrease all indexs >= current index by 1
                # but first remove the change we've been working with 
                popped_index = index_changes.pop(change_index)
                # now decrease indexes 
                index_changes = {(k-1 if k > change_index else k): v for k, v in index_changes.items()}
                # adjust the changes_tuples list
                popped_change_tup = changes_tuples.pop(i)
                # update the indexes in change tuples as well now
                changes_tuples = [((ct[0], ct[1], ct[2]-1) if ct[2] > change_index else ct) for ct in changes_tuples]
                # don't increment i because we've decreased the changes_tuple list so i should now be pointing at the next item
            elif right_delta_ins > 0 and right_delta_edit > 0:
                created_compound += 1
                # adjust the reference to have the "compound" but keep a space so the character comparison will realize the change 
                ref[change_index+1] = change_tup[0] + ' ' + ref[change_index+1]
                # remove the extra word and deletion space
                popped_ref = ref.pop(change_index)
                popped_hyp = hyp.pop(change_index)
                # update the change indexes...
                # since we've removed a word we'll need to decrease all indexs >= current index by 1
                # but first remove the change we've been working with 
                popped_index = index_changes.pop(change_index)
                # now decrease indexes 
                index_changes = {(k-1 if k > change_index else k): v for k, v in index_changes.items()}
                # adjust the changes_tuples list
                popped_change_tup = changes_tuples.pop(i)
                # update the indexes in change tuples as well now
                changes_tuples = [((ct[0], ct[1], ct[2]-1) if ct[2] > change_index else ct) for ct in changes_tuples]
                # don't increment i because we've decreased the changes_tuple list so i should now be pointing at the next item
            else:
                # attempting to attach word to either neighborning word has made things worse...ergo we'll not do anything
                i += 1
        else:
            # this is a substitution pair so we'll pass
            i += 1
    return changes_tuples, index_changes, ref, hyp, created_compound, brokeup_compound