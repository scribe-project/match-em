import Levenshtein
import pandas as pd
import numpy as np
from copy import deepcopy
from operator import itemgetter
from itertools import chain

from .character_distances import get_norwegian_character_sub_cost


def get_character_error_rate(ref, hyp):
    if len(ref) > 0:
        return len(Levenshtein.editops(ref, hyp)) / len(ref)
    else:
        return(0)

def get_sub_cost(word1, word2, allow_greater_than_1=False):
    # allowing a sub cost > 1 means that insertions/deletions will be favoured instead of alignment of dissimilar words
    if allow_greater_than_1:
        return get_character_error_rate(word1, word2)
    else:
        # we don't necessarily want a cost larger than 1 so we'll return the CER
        # if it's smaller than 1 else 1
        return min(1, get_character_error_rate(word1, word2))

def paths_not_ending_at_zero(paths):
    if len(paths) == 0:
        return True
    paths_not_done = [path for path in paths if path[-1] != 0]
    if paths_not_done == []:
        return False
    return True

def trim_candiate_list(paths, n):
    # keep the n shortest paths
    if len(paths) <= n:
        return paths
    return [p[0] for p in sorted([(path, len(path)) for path in paths], key=itemgetter(1))[:n]]


class distance():

    def generate_matrixes(self):
        distance_matrix = np.zeros((len(self.hyp) + 1, len(self.ref) + 1))

        # set values for all inserts/deletes
        distance_matrix[0, :] = list(range(len(self.ref) + 1)) # set the first row (insertions)
        distance_matrix[: ,0] = list(range(len(self.hyp) + 1)) # set the first column (deletions)
        distance_matrix

        backtrace_array = [[0 for x in range(len(self.ref) + 1)] for y in range(len(self.hyp) + 1)] 
        for x in range(1, len(self.hyp) + 1):
            backtrace_array[x][0] = (x-1, 0)
        for x in range(1, len(self.ref) + 1):
            backtrace_array[0][x] = (0, x-1)

        self.distance_matrix = distance_matrix
        self.backtrace_array = backtrace_array

    def check_all_backtrace_paths_are_lists(self):
        for i in range(len(self.backtrace_array)):
            for j in range(len(self.backtrace_array[i])):
                if i != 0 and j != 0:
                    if not isinstance(self.backtrace_array[i][j], list):
                        self.backtrace_array[i][j] = [self.backtrace_array[i][j]]

    def compute_unweighted_alignment(self):
        # generate new, clean matrixes
        self.generate_matrixes()

        ### ORIGINAL, unweighted, matrix
        for j in range(1, len(self.ref) + 1):
            for i in range(1, len(self.hyp) + 1):
                if self.ref[j-1] == self.hyp[i-1]:
                    sub_cost = 0
                else:
                    sub_cost = 1
                min_alignment = min(
                    self.distance_matrix[i-1, j] + 1,            # deletion
                    self.distance_matrix[i, j-1] + 1,            # insertion 
                    self.distance_matrix[i-1, j-1] + sub_cost    # substitution
                )
                self.distance_matrix[i, j] = min_alignment
                # store pointers
                pointers = []
                if self.distance_matrix[i-1, j] + 1 == min_alignment:
                    pointers.append((i-1, j))
                if self.distance_matrix[i, j-1] + 1 == min_alignment:
                    pointers.append((i, j-1))
                if self.distance_matrix[i-1, j-1] + sub_cost == min_alignment:
                    pointers.append((i-1, j-1))
                self.backtrace_array[i][j] = pointers

    def compute_weighted_word_alignment(self, allow_greater_than_1=False):
        # generate new, clean matrixes
        self.generate_matrixes()

        ### NEW weighted matrix
        for j in range(1, len(self.ref) + 1):
            for i in range(1, len(self.hyp) + 1):
                if self.ref[j-1] == self.hyp[i-1]:
                    sub_cost = 0
                else:
                    sub_cost = get_sub_cost(self.ref[j-1],self.hyp[i-1], allow_greater_than_1=allow_greater_than_1)
                min_alignment = min(
                    self.distance_matrix[i-1, j] + 1,            # deletion
                    self.distance_matrix[i, j-1] + 1,            # insertion 
                    self.distance_matrix[i-1, j-1] + sub_cost    # substitution
                )
                self.distance_matrix[i, j] = min_alignment
                # store pointers
                pointers = []
                if self.distance_matrix[i-1, j] + 1 == min_alignment:
                    pointers.append((i-1, j))
                if self.distance_matrix[i, j-1] + 1 == min_alignment:
                    pointers.append((i, j-1))
                if self.distance_matrix[i-1, j-1] + sub_cost == min_alignment:
                    pointers.append((i-1, j-1))
                self.backtrace_array[i][j] = pointers

    def compute_weighted_character_alignment(self):
        # i hope this doesn't mess something else up?
        self.ref = self.ref[0]
        self.hyp = self.hyp[0]

        # generate new, clean matrixes
        self.generate_matrixes()

        ### NEW weighted matrix
        for j in range(1, len(self.ref) + 1):
            for i in range(1, len(self.hyp) + 1):
                if self.ref[j-1] == self.hyp[i-1]:
                    sub_cost = 0
                else:
                    sub_cost = get_norwegian_character_sub_cost(self.ref[j-1],self.hyp[i-1])
                min_alignment = min(
                    self.distance_matrix[i-1, j] + 1,            # deletion
                    self.distance_matrix[i, j-1] + 1,            # insertion 
                    self.distance_matrix[i-1, j-1] + sub_cost    # substitution
                )
                self.distance_matrix[i, j] = min_alignment
                # store pointers
                pointers = []
                if self.distance_matrix[i-1, j] + 1 == min_alignment:
                    pointers.append((i-1, j))
                if self.distance_matrix[i, j-1] + 1 == min_alignment:
                    pointers.append((i, j-1))
                if self.distance_matrix[i-1, j-1] + sub_cost == min_alignment:
                    pointers.append((i-1, j-1))
                self.backtrace_array[i][j] = pointers

    def backtrace_alignment_paths(self):
        i, j = [s-1 for s in self.distance_matrix.shape] # take off 1 for zero indexing
        paths = [[(i, j)]]
        keep_top = 5

        while paths_not_ending_at_zero(paths):
            new_paths = []
            for path in paths:
                current_path = deepcopy(path)
                last_state = path[-1]
                if last_state != 0:
                    next_target = self.backtrace_array[last_state[0]][last_state[1]]
                    # idk how but we got (0, 1) as the next target instead of [(0, 1)] and it caused errors so this is slapping a fix on it
                    if isinstance(next_target, tuple):
                        next_target = [next_target]
                    if next_target == 0:
                        new_path = current_path + [next_target]
                        new_paths.append(new_path)
                    else:
                        for target in next_target:
                            new_path = current_path + [target]
                            new_paths.append(new_path)
                else:
                    new_paths.append(current_path)
            paths = trim_candiate_list(new_paths, keep_top)
        return paths

    def create_editops(self, path):
        previous_i = np.nan
        previous_j = np.nan
        ops = []

        if path[0] != 0:
            path = list(reversed(deepcopy(path)))
        # get rid of the starting 0, we shouldn't need it anymore
        path.pop(0)
        # things can get weird if the first word was deleted
        if path[0] != (0,0):
            path = [(0,0)] + path

        for move in path:
            # because we're working with index-1 we'll skip (0,0)
            if move != (0, 0):
                if move[0] == previous_i:
                    # ops.append(('delete', move[0]-1, move[1]-1))
                    ops.append(('delete', move[1]-1, move[0]-1))
                elif move[1] == previous_j:
                    # ops.append(('insert', move[0]-1, move[1]-1))
                    ops.append(('insert', move[1]-1, move[0]-1))
                else:
                    if self.hyp[move[0]-1] != self.ref[move[1]-1]:
                        # ops.append(('sub', move[0]-1, move[1]-1))
                        ops.append(('sub', move[1]-1, move[0]-1))
            previous_i = move[0]
            previous_j = move[1]
        return ops

    def get_unweighted_editops(self):
        self.compute_unweighted_alignment()
        candidate_paths = self.backtrace_alignment_paths()
        if len(candidate_paths) > 1:
            # TODO decide which alignment we like most
            path = candidate_paths[0]
        else:
            path = candidate_paths[0]
        editops = self.create_editops(path)
        return editops

    def get_weighted_editops(self, allow_greater_than_1=False):
        self.compute_weighted_word_alignment(allow_greater_than_1=allow_greater_than_1)
        candidate_paths = self.backtrace_alignment_paths()
        if len(candidate_paths) > 1:
            # TODO decide which alignment we like most
            path = candidate_paths[0]
        else:
            path = candidate_paths[0]
        editops = self.create_editops(path)
        return editops

    def get_weighted_character_editops(self):
        self.compute_weighted_character_alignment()
        candidate_paths = self.backtrace_alignment_paths()
        if len(candidate_paths) > 1:
            # TODO decide which alignment we like most
            path = candidate_paths[0]
        else:
            path = candidate_paths[0]
        editops = self.create_editops(path)
        return editops

    def get_levenshtein_editops(self):
        # tokenize each word into an integer
        vocabulary = list(set(chain(self.ref, self.hyp)))

        word2char = {vocabulary[vocab_number]: chr(vocab_number) for vocab_number in range(len(vocabulary))}

        truth_chars = "".join([word2char[w] for w in self.ref])
        hypothesis_chars = "".join([word2char[w] for w in self.hyp])

        editops = Levenshtein.editops(truth_chars, hypothesis_chars)
        return editops

    def __init__(self, ref: str, hyp: str) -> None:
        ref = deepcopy(ref)
        hyp = deepcopy(hyp)

        # split on spaces (if they're not already split)
        if isinstance(ref, str):
            ref = ref.split(' ')
        if isinstance(hyp, str):
            hyp = hyp.split(' ')
        self.ref = ref
        self.hyp = hyp
