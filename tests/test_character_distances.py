import numpy as np
import unittest

import match_em.character_distances as character_distances

class character_distances_test(unittest.TestCase):

    def test_char_lookup(self):
        char_traits = character_distances.character_traits()
        (char_type, char_vector) = char_traits.lookup_character('a')
        self.assertEqual(char_type, 'vowels')
        self.assertEqual(str([2,0,0]), str(char_vector))

    def test_char_distances_i_a(self):
        dist = character_distances.norwegian_character_distance(
            [0, 2, 0],
            [2, 0, 0]
        )
        self.assertEqual(np.sqrt(8), dist)
    def test_char_distances_i_y(self):
        dist = character_distances.norwegian_character_distance(
            [0, 2, 0],
            [0, 2, 1]
        )
        self.assertEqual(1, dist)
    def test_char_distances_t_t(self):
        dist = character_distances.norwegian_character_distance(
            [0, 0, 0, 2, 0],
            [0, 0, 0, 2, 0]
        )
        self.assertEqual(0, dist)
    def test_char_distances_d_t(self):
        dist = character_distances.norwegian_character_distance(
            [0, 0, 0, 2, 0],
            [1, 0, 0, 2, 0]
        )
        self.assertEqual(1, dist)
    def test_char_distances_b_g(self):
        dist = character_distances.norwegian_character_distance(
            [1, 0, 0, 0, 0],
            [1, 0, 0, 5, 0]
        )
        self.assertEqual(5, dist)
    def test_char_distances_s_c(self):
        dist = character_distances.norwegian_character_distance(
            [0, 2, 0, 2, 0],
            [
                [0, 0, 0, 5, 0],
                [0, 2, 0, 2, 0]
            ]
        )
        self.assertEqual(0, dist)
    def test_char_distances_r_c(self):
        dist = character_distances.norwegian_character_distance(
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
        sub_cost = character_distances.get_norwegian_character_sub_cost('a', 'a')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_a_o(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost('a', 'o')
        self.assertEqual(
            np.sqrt(5) / np.sqrt(np.square(2) + np.square(2) + np.square(2)),
            sub_cost
        )
    def test_sub_cost_t_t(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost('t', 't')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_t_d(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost('t', 'd')
        self.assertEqual(
            1 / np.sqrt(np.square(1) + np.square(3) + np.square(1) + np.square(7) + np.square(1)),
            sub_cost
        )
    def test_sub_cost_a_t(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost('a', 't')
        self.assertEqual(sub_cost, 1)
    def test_sub_cost_a_l(self):
        # discount from 1 bc vowel and liquid
        sub_cost = character_distances.get_norwegian_character_sub_cost('a', 'l')
        self.assertEqual(sub_cost, 0.9)

    def test_sub_cost_spc_spc(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost(' ', ' ')
        self.assertEqual(sub_cost, 0)
    def test_sub_cost_spc_a(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost(' ', 'a')
        self.assertEqual(sub_cost, 1)
    def test_sub_cost_spc_b(self):
        sub_cost = character_distances.get_norwegian_character_sub_cost(' ', 'b')
        self.assertEqual(sub_cost, 1)

if __name__ == '__main__':
    unittest.main()

