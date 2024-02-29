import numpy as np
import unittest

import match_em
from char_traits import character_distances

class character_distances_test(unittest.TestCase):

    def test_char_lookup(self):
        char_traits = character_distances('no')
        (char_type, char_vector) = char_traits.get_character_type_and_vector('a')
        self.assertEqual(char_type, 'vowels')
        self.assertEqual(str([2,0,0]), str(char_vector))

    def test_char_lookup_é(self):
        char_traits = character_distances('no')
        (char_type, char_vector) = char_traits.get_character_type_and_vector('é')
        self.assertEqual(char_type, 'vowels')
        self.assertEqual(str([1,2,0]), str(char_vector))

    def test_char_distances_i_a(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [0, 2, 0],
            [2, 0, 0]
        )
        self.assertEqual(np.sqrt(8), dist)
    def test_char_distances_i_y(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [0, 2, 0],
            [0, 2, 1]
        )
        self.assertEqual(1, dist)
    def test_char_distances_t_t(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [0, 0, 0, 2, 0],
            [0, 0, 0, 2, 0]
        )
        self.assertEqual(0, dist)
    def test_char_distances_d_t(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [0, 0, 0, 2, 0],
            [1, 0, 0, 2, 0]
        )
        self.assertEqual(1, dist)
    def test_char_distances_b_g(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [1, 0, 0, 0, 0],
            [1, 0, 0, 5, 0]
        )
        self.assertEqual(5, dist)
    def test_char_distances_s_c(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [0, 2, 0, 2, 0],
            [
                [0, 0, 0, 5, 0],
                [0, 2, 0, 2, 0]
            ]
        )
        self.assertEqual(0, dist)
    def test_char_distances_r_c(self):
        char_traits = character_distances('no')
        dist = char_traits.calculate_character_distance(
            [
                [1, 1, 0, 2, 0],
                [1, 1, 0, 6, 0]
            ],
            [
                [0, 0, 0, 5, 0],
                [0, 2, 0, 2, 0]
            ]
        )
        self.assertEqual(np.sqrt(2), dist)

    def test_sub_cost_a_a(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('a', 'a')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_a_o(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('a', 'o')
        self.assertEqual(
            np.sqrt(5) / np.sqrt(np.square(2) + np.square(2) + np.square(2)),
            sub_cost
        )
    def test_sub_cost_t_t(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('t', 't')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_t_d(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('t', 'd')
        self.assertEqual(
            1 / np.sqrt(np.square(1) + np.square(3) + np.square(1) + np.square(7) + np.square(1)),
            sub_cost
        )
    def test_sub_cost_a_t(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('a', 't')
        self.assertEqual(sub_cost, 1)
    def test_sub_cost_a_l(self):
        # discount from 1 bc vowel and liquid
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost('a', 'l')
        self.assertEqual(sub_cost, 0.9)

    def test_sub_cost_spc_spc(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost(' ', ' ')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_spc_a(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost(' ', 'a')
        self.assertEqual(sub_cost, 1)
    def test_sub_cost_spc_b(self):
        char_traits = character_distances('no')
        sub_cost = char_traits.get_character_sub_cost(' ', 'b')
        self.assertEqual(sub_cost, 1)

if __name__ == '__main__':
    unittest.main()

