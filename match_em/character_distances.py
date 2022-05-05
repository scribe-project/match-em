import json
import numpy as np

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

from . import character_data

def _read_character_traits() -> set:
    return json.loads(pkg_resources.read_text(character_data, 'character_traits.json'))

class character_traits:
    def lookup_character(self, char):
        if char in self.character_details['vowels']:
            return ('vowels', self.character_details['vowels'][char])
        elif char in self.character_details['consonants']:
            return ('consonants', self.character_details['consonants'][char])
        else:
            raise Exception('Unknown character: {}'.format(char))
    
    def __init__(self):
        self.character_details = _read_character_traits()

def norwegian_character_distance(v1, v2):
    # just euclidian distance
    if isinstance(v1[0], tuple) or isinstance(v1[0], list):
        distances = []
        for v1_tup in v1:
            distances.append(norwegian_character_distance(v1_tup, v2))
        return min(distances)
    elif isinstance(v2[0], tuple) or isinstance(v2[0], list):
        distances = []
        for v2_tup in v2:
            distances.append(norwegian_character_distance(v1, v2_tup))
        return min(distances)
    else:
        dist = np.sqrt(
            # NOTE this is only designed to work with V1 and V2 being the same length
            sum([np.square(v1[i] - v2[i]) for i in range(len(v1))])
        )
        return dist

def get_norwegian_character_sub_cost(char1, char2):
    char_traits = character_traits()
    (char1_type, char1_vector) = char_traits.lookup_character(char1)
    (char2_type, char2_vector) = char_traits.lookup_character(char2)
    if char1_type == char2_type:
        # NOTE we're doing normalization on these values so we don't end up with a sub cost of like 7...
        if char1_type == 'vowels':
            # if how we define vowels change this will need to change too
            max_vowel_difference = np.sqrt(np.square(2) + np.square(2) + np.square(2))
            char_diff = norwegian_character_distance(char1_vector, char2_vector)
            return char_diff / max_vowel_difference
        else:
            # if, for some reason, we have something other than a vowel or consonant this isn't checking for it lol
            # if how we define consonants change this will need to change too
            max_consonant_difference = np.sqrt(np.square(1) + np.square(3) + np.square(1) + np.square(7) + np.square(1))
            char_diff = norwegian_character_distance(char1_vector, char2_vector)
            return char_diff / max_consonant_difference
    else:
        # we'll slightly lower the cost of subbing a vowel and approximant since they're gestually similar 
        if char1_type == 'consonants' and char1_vector[1] == 3:
            # i just chose this number. idk if it's "right"
            return 0.75
        elif char2_type == 'consonants' and char2_vector[1] == 3:
            return 0.75
        else:
            return 1
