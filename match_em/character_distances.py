import json
import numpy as np
import pandas as pd

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

def _read_character_traits(langugage: str) -> set:
    loaded_json = json.loads(pkg_resources.read_text(character_data, 'character_traits.json'))
    if langugage in loaded_json:
        return loaded_json[langugage]
    raise Exception('Unknown language: {}. Please either use one of {} or define a new language'.format(
        langugage,
        list(loaded_json.keys())
    ))

class character_distances:
    def calculate_character_distance(self, v1, v2):
        # just euclidian distance
        if isinstance(v1[0], tuple) or isinstance(v1[0], list):
            distances = []
            for v1_tup in v1:
                distances.append(self.calculate_character_distance(v1_tup, v2))
            return min(distances)
        elif isinstance(v2[0], tuple) or isinstance(v2[0], list):
            distances = []
            for v2_tup in v2:
                distances.append(self.calculate_character_distance(v1, v2_tup))
            return min(distances)
        else:
            dist = np.sqrt(
                # NOTE this is only designed to work with V1 and V2 being the same length
                sum([np.square(v1[i] - v2[i]) for i in range(len(v1))])
            )
            return dist

    def get_character_type_and_vector(self, char):
        if char in self.character_details['vowels']:
            return ('vowels', self.character_details['vowels'][char])
        elif char in self.character_details['consonants']:
            return ('consonants', self.character_details['consonants'][char])
        elif char in self.character_details['spaces']:
            return ('spaces', self.character_details['spaces'][char])
        elif char in self.character_details['punctuation']:
            return ('punctuation', self.character_details['punctuation'][char])
        else:
            raise Exception('Unknown character: {}'.format(char))

    def build_character_distance_table(self):
        char_to_index = {}
        i_count = 0
        for char_type in self.character_details:
            for char in self.character_details[char_type]:
                char_to_index[char] = i_count
                i_count += 1
        character_table = np.full((len(char_to_index), len(char_to_index)), fill_value=np.nan)
        for char_a in char_to_index.keys():
            (char_a_type, char_a_vector) = self.get_character_type_and_vector(char_a)
            for char_b in char_to_index.keys():
                (char_b_type, char_b_vector) = self.get_character_type_and_vector(char_b)
                if char_a_type == char_b_type:
                    # NOTE we're doing normalization on these values so we don't end up with a sub cost of like 7...
                    if char_a_type == 'vowels':
                        # if how we define vowels change this will need to change too
                        max_vowel_difference = np.sqrt(np.square(2) + np.square(2) + np.square(2))
                        char_diff = self.calculate_character_distance(char_a_vector, char_b_vector)
                        sub_score = char_diff / max_vowel_difference
                    elif char_a_type == 'consonants':
                        # if how we define consonants change this will need to change too
                        max_consonant_difference = np.sqrt(np.square(1) + np.square(3) + np.square(1) + np.square(7) + np.square(1))
                        char_diff = self.calculate_character_distance(char_a_vector, char_b_vector)
                        sub_score = char_diff / max_consonant_difference
                    elif char_a_type == 'punctuation':
                        # TODO: care about punctuation in the future
                        sub_score = 0
                    else:
                        # dealing with spaces 
                        sub_score = 0
                else:
                    # we'll slightly lower the cost of subbing a vowel and approximant since they're gestually similar 
                    if char_b_type == 'vowels' and (char_a_type == 'consonants' and char_a_vector[1] == 4):
                        # i just chose this number. idk if it's "right"
                        sub_score = 0.9
                    elif char_a_type == 'vowels' and (char_b_type == 'consonants' and char_b_vector[1] == 4):
                        sub_score = 0.9
                    else:
                        sub_score = 1
                character_table[char_to_index[char_a], char_to_index[char_b]] = sub_score
        self.character_table = pd.DataFrame(character_table, index=char_to_index.keys(), columns=char_to_index.keys())

    def get_character_sub_cost(self, char1, char2):
        return self.character_table.loc[char1, char2]
    
    def __init__(self, language):
        self.character_details = _read_character_traits(language)
        self.build_character_distance_table()
    