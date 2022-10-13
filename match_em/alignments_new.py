from copy import deepcopy
from dataclasses import dataclass
from distutils.command import clean

from .distances import distance
import Levenshtein
import re

def update_change_tuples(change_tuples, index_greater_than, change_by=-1):
    change_by = int(change_by)
    return [(ct[0], ct[1], ct[2] + change_by if ct[2] > index_greater_than else ct[2]) for ct in change_tuples]

def fix_del_ins_series(ref, hyp, change_tuples):
    # we want to exclude the last item because we look at the +1 tuple to try to combine
    for i in range(len(change_tuples) - 1):
        change_tup = change_tuples[i]
        if change_tup[0] == ' ':
            next_tup = change_tuples[i+1]
            if next_tup[1] == ' ':
                # update the ref and hyp
                ref.pop(change_tup[2])
                hyp.pop(next_tup[2])
                # do the combine!
                change_tuples[i] = (
                    next_tup[0],
                    change_tup[1],
                    change_tup[2]
                )
                change_tuples.pop(i+1)
                change_tuples = update_change_tuples(change_tuples, change_tup[2])
                return(fix_del_ins_series(ref, hyp, change_tuples))
        elif change_tup[1] == ' ':
            next_tup = change_tuples[i+1]
            if next_tup[0] == ' ':
                # update the ref and hyp
                hyp.pop(change_tup[2])
                ref.pop(next_tup[2])
                # do the combine
                change_tuples[i] = (
                    change_tup[0],
                    next_tup[1],
                    change_tup[2]
                )
                change_tuples.pop(i+1)
                change_tuples = update_change_tuples(change_tuples, change_tup[2])
                return(fix_del_ins_series(ref, hyp, change_tuples))
    return ref, hyp, change_tuples


shifting_to_index = {
    "ref" : 0,
    "hyp" : 1
}

spaces_pattern = re.compile("\s+")

def remove_spaces(word):
    return spaces_pattern.sub('', word)

def get_character_del_count(ref, hyp):
    return len([edtop for edtop in Levenshtein.editops(ref, hyp) if edtop[0] == 'delete'])
    # return len([edtop for edtop in distance(ref, hyp).get_weighted_character_editops() if edtop[0] == 'delete'])

def get_character_ins_count(ref, hyp):
    return len([edtop for edtop in Levenshtein.editops(ref, hyp) if edtop[0] == 'insert'])
    # return len([edtop for edtop in distance(ref, hyp).get_weighted_character_editops() if edtop[0] == 'insert'])

def get_character_change_count(ref, hyp):
    return len([edtop for edtop in Levenshtein.editops(remove_spaces(ref), remove_spaces(hyp))])
    # return len([edtop for edtop in distance(ref, hyp).get_weighted_character_editops()])

def get_shifting_opposite(shifting_index):
    if shifting_index == 0:
        return 1
    return 0

def shift_left(token_lists, change_tuples, shifting):
    base_token_lists = deepcopy(token_lists)
    shifting_tokens = token_lists.pop(shifting_to_index[shifting])
    # we'll have popped out the other one
    staying_tokens = token_lists[0]
    # since we're shifting left we can't left-shift the first word
    for i in range(1, len(change_tuples)):
        change_tup = change_tuples[i]
        if change_tup[shifting_to_index[shifting]] != ' ':
            for shift_amount in range(1, (i+1)):
                prev_staying_token = staying_tokens[change_tup[2] - shift_amount]
                prev_shifting_token = shifting_tokens[change_tup[2] - shift_amount]
                base_cer = get_character_change_count(prev_staying_token, prev_shifting_token)
                new_cer = get_character_change_count(prev_staying_token, prev_shifting_token + change_tup[shifting_to_index[shifting]])
                if new_cer < base_cer:
                    new_token = prev_shifting_token + ' ' + change_tup[shifting_to_index[shifting]]
                    shifting_tokens[change_tup[2] - shift_amount] = new_token
                    # first update the prev change tuple
                    prev_change_tup = change_tuples[i - shift_amount]
                    # there was already a change for the word, we'll just add to it
                    if prev_change_tup[2] == change_tup[2] - shift_amount:
                        if new_token.strip() == prev_change_tup[get_shifting_opposite(shifting_to_index[shifting])].strip():
                            # we've aligned 2 words that are exactly the same and we don't need this change tuple
                            change_tuples.pop(i - shift_amount)
                            # we don't need to update the change tuples further because we've not modified the number of tokens 
                            # we we have changed change_tuples so we'll need to update the index
                            i -= 1
                        else:
                            new = ['', '', prev_change_tup[2]]
                            new[shifting_to_index[shifting]] = new_token
                            new[get_shifting_opposite(shifting_to_index[shifting])] = prev_change_tup[get_shifting_opposite(shifting_to_index[shifting])]
                            change_tuples[i - shift_amount] = tuple(new)
                    # is this now completely illegible...maybe...
                    # bascially we want to check if the other word in the change tuple was a real word of a blank
                    if change_tup[get_shifting_opposite(shifting_to_index[shifting])] == ' ':
                        # get rid of the unnecessary token
                        shifting_tokens.pop(change_tup[2])
                        # this means we'll want to remove the tuple as well as the empty space from the staying tokens
                        change_tuples.pop(i)
                        staying_tokens.pop(change_tup[2])
                        change_tuples = update_change_tuples(change_tuples, index_greater_than=change_tup[2] - 1)
                    else:
                        # update the word we moved to a blank
                        shifting_tokens[change_tup[2]] = ' '
                        # let it stand as an insertion
                        new = ['', '', change_tup[2]]
                        new[shifting_to_index[shifting]] = ' '
                        new[get_shifting_opposite(shifting_to_index[shifting])] = change_tup[get_shifting_opposite(shifting_to_index[shifting])]
                        change_tuples[i] = tuple(new)
                    new_token_list = ['', '']
                    new_token_list[shifting_to_index[shifting]] = shifting_tokens
                    new_token_list[get_shifting_opposite(shifting_to_index[shifting])] = staying_tokens
                    return(shift_left(new_token_list, change_tuples, shifting))
                else:
                    # we'll keep trying to shift as long as there's no word in our way
                    if prev_shifting_token != ' ':
                        break

    return base_token_lists, change_tuples, shifting

def shift_right(token_lists, change_tuples, shifting):
    base_token_lists = deepcopy(token_lists)
    shifting_tokens = token_lists.pop(shifting_to_index[shifting])
    # we'll have popped out the other one
    staying_tokens = token_lists[0]
    # since we're shifting right we can't right-shift the last word
    for i in range(len(change_tuples)-1):
        change_tup = change_tuples[i]
        if change_tup[shifting_to_index[shifting]] != ' ':
            diff = len(staying_tokens) - change_tup[2] 
            for shift_amount in range(1, diff):
                next_staying_token = staying_tokens[change_tup[2] + shift_amount]
                next_shifting_token = shifting_tokens[change_tup[2] + shift_amount]
                base_cer = get_character_change_count(next_staying_token, next_shifting_token)
                new_cer = get_character_change_count(next_staying_token, change_tup[shifting_to_index[shifting]] + next_shifting_token)
                if new_cer < base_cer:
                    new_token = change_tup[shifting_to_index[shifting]] + ' ' + next_shifting_token
                    shifting_tokens[change_tup[2] + shift_amount] = new_token
                    # first update the next change tuple
                    next_change_tup = change_tuples[i + shift_amount]
                    # there was already a change for the word, we'll just add to it
                    if next_change_tup[2] == change_tup[2] + shift_amount:
                        if new_token.strip() == next_change_tup[get_shifting_opposite(shifting_to_index[shifting])].strip():
                            # we've aligned 2 words that are exactly the same and we don't need this change tuple
                            change_tuples.pop(i + shift_amount)
                            # now update the index that's tracking change_tuples
                            i -= 1
                        else:
                            new = ['', '', next_change_tup[2]]
                            new[shifting_to_index[shifting]] = new_token
                            new[get_shifting_opposite(shifting_to_index[shifting])] = next_change_tup[get_shifting_opposite(shifting_to_index[shifting])]
                            change_tuples[ i+ shift_amount] = tuple(new)
                    # is this now completely illegible...maybe...
                    # bascially we want to check if the other word in the change tuple was a real word of a blank
                    if change_tup[get_shifting_opposite(shifting_to_index[shifting])] == ' ':
                        # now get rid of the token we added
                        shifting_tokens.pop(change_tup[2])
                        # this means we'll want to remove the tuple as well as the empty space from the staying tokens
                        change_tuples.pop(i)
                        staying_tokens.pop(change_tup[2])
                        change_tuples = update_change_tuples(change_tuples, index_greater_than=change_tup[2])
                    else:
                        # update the word we moved to a blank
                        shifting_tokens[change_tup[2]] = ' '
                        # let it stand as an insertion
                        new = ['', '', change_tup[2]]
                        new[shifting_to_index[shifting]] = ' '
                        new[get_shifting_opposite(shifting_to_index[shifting])] = change_tup[get_shifting_opposite(shifting_to_index[shifting])]
                        change_tuples[i] = tuple(new)
                    shifting_tokens, staying_tokens, change_tuples = fix_del_ins_series(shifting_tokens, staying_tokens, change_tuples)
                    new_token_list = ['', '']
                    new_token_list[shifting_to_index[shifting]] = shifting_tokens
                    new_token_list[get_shifting_opposite(shifting_to_index[shifting])] = staying_tokens
                    return(shift_right(new_token_list, change_tuples, shifting))
                else:
                    # we'll keep trying to shift as long as there's no word in our way 
                    if next_shifting_token != ' ':
                        break
    return base_token_lists, change_tuples, shifting

def count_compounds_created_broken(change_tuples):
    created_count = 0
    created_joins = 0
    broken_count = 0
    broken_joins = 0 
    has_word_pattern = re.compile(r'^\w')
    for change_tup in change_tuples:
        if has_word_pattern.search(change_tup[0]):
            created_count += 1 if ' ' in change_tup[0] else 0
            created_joins += change_tup[0].count(' ')
        if has_word_pattern.search(change_tup[1]):
            broken_count +=  1 if ' ' in change_tup[1] else 0
            broken_joins += change_tup[1].count(' ')
    return created_count, broken_count, created_joins, broken_joins

def generate_index_changes(change_tuples):
    return {change_tup[2] : 'S' if change_tup[0] != ' ' and change_tup[1] != ' ' else ' ' for change_tup in change_tuples}

def strip_whitespace_item(item):
    if item != ' ':
        return item.strip()
    return item

def clean_tokens(tokens):
    return [strip_whitespace_item(word) for word in tokens]

def clean_change_tuples(change_tuples):
    return[(strip_whitespace_item(change_tup[0]), strip_whitespace_item(change_tup[1]), change_tup[2]) for change_tup in change_tuples]

def check_word_compounding(ref, hyp, change_tuples):
    still_changing = True
    token_lists = [ref, hyp]
    while still_changing:
        org_tokens = deepcopy(token_lists)
        # try shifting ref left
        token_lists, change_tuples, _ = shift_left(token_lists, change_tuples, 'ref')
        # try shifting ref right
        token_lists, change_tuples, _ = shift_right(token_lists, change_tuples, 'ref')
        # try shifting hyp left 
        token_lists, change_tuples, _ = shift_left(token_lists, change_tuples, 'hyp')
        # try shifting hyp right
        token_lists, change_tuples, _ = shift_right(token_lists, change_tuples, 'hyp')
        # keep trying to shift as long as there's more shifts to be found
        token_lists = [clean_tokens(token_lists[0]), clean_tokens(token_lists[1])]
        if org_tokens == token_lists:
            still_changing = False
    
    ref = token_lists[0]
    hyp = token_lists[1]
    change_tuples = clean_change_tuples(change_tuples)
    created_count, broken_count, created_joins, broken_joins = count_compounds_created_broken(change_tuples)
    
    return ref, hyp, change_tuples, generate_index_changes(change_tuples), created_count, broken_count, created_joins, broken_joins