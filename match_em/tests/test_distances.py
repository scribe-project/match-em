import numpy as np
import unittest

import match_em
from match_em.character_distances import character_distances

class AlignmentsTests(unittest.TestCase):

    def test_get_character_error_rate_one_sub(self):
        cer = match_em.distances.get_character_error_rate('hello', 'hallo')
        self.assertEqual(cer, 1/5)
    def test_get_character_error_rate_one_del(self):
        cer = match_em.distances.get_character_error_rate('hello', 'hell')
        self.assertEqual(cer, 1/5)
    def test_get_character_error_rate_one_ins(self):
        cer = match_em.distances.get_character_error_rate('hello', 'helloo')
        self.assertEqual(cer, 1/5)
    def test_get_character_error_rate_all_sub(self):
        cer = match_em.distances.get_character_error_rate('hello', 'shows')
        self.assertEqual(cer, 1)
    def test_get_character_error_rate_all_del(self):
        cer = match_em.distances.get_character_error_rate('hello', '')
        self.assertEqual(cer, 1)
    def test_get_character_error_rate_all_ins(self):
        cer = match_em.distances.get_character_error_rate('', 'hallo')
        self.assertEqual(cer, 0)

    def test_get_sub_cost_greater_than_1(self):
        '''
        Testing the substitution cost when the CER should be > 1
        NOTE: the current expected behaviour for CER > 1 is to return 1. If that changes this test needs to be updated
        '''
        cost = match_em.distances.get_sub_cost('test', 'calibration')
        self.assertEqual(cost, 1)
    def test_get_sub_cost_less_than_1(self):
        '''
        Testing the substitution cost when the CER should be < 1. Expectation is that the CER is returned
        '''
        cost = match_em.distances.get_sub_cost('test', 'tests')
        self.assertEqual(cost, 1/4)

    def test_paths_not_ending_at_zero_no_paths(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([])
        self.assertEqual(end_in_zero, True)
    def test_paths_not_ending_at_zero_one_path_not_zero(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([[(1,1), (0,0)]])
        self.assertEqual(end_in_zero, True)
    def test_paths_not_ending_at_zero_one_path_yes_zero(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([[(1,1), (0,0), 0]])
        self.assertEqual(end_in_zero, False)
    def test_paths_not_ending_at_zero_many_path_one_yes_zero(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([[(1,1), (0,0), 0], [(1,1), (0,0)]])
        self.assertEqual(end_in_zero, True)
    def test_paths_not_ending_at_zero_many_path_all_yes_zero(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([[(1,1), (0,0), 0], [(1,1), (0,0), 0]])
        self.assertEqual(end_in_zero, False)
    def test_paths_not_ending_at_zero_many_path_all_not_zero(self):
        end_in_zero = match_em.distances.paths_not_ending_at_zero([[(1,1), (0,0)], [(1,1), (0,0)]])
        self.assertEqual(end_in_zero, True)

    def test_trim_candiate_list_needs_trim(self):
        paths = match_em.distances.trim_candiate_list(
            [
                (1,2,3),
                (4,5,6),
                (7,8),
                (1,2,3,4),
                (4,5,6,7),
                (2,6,4)
            ]
        , 5)
        self.assertEqual(len(paths), 5)
    def test_trim_candiate_list_doesntneed_trim(self):
        paths = match_em.distances.trim_candiate_list(
            [
                (1,2,3),
                (4,5,6),
                (7,8),
                (1,2,3,4)
            ]
        , 5)
        self.assertEqual(len(paths), 4)

    def test_generate_matrix(self):
        dist = match_em.distances.distance('this is a test', 'a test this is', character_distances('no'))
        dist.generate_matrixes()
        distance_matrix = np.array([
            [0, 1, 2, 3, 4],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [3, 0, 0, 0, 0],
            [4, 0, 0, 0, 0]
        ])
        backtrace_array = [
            [0, (0,0), (0,1), (0,2), (0,3)],
            [(0,0), 0, 0, 0, 0],
            [(1,0), 0, 0, 0, 0],
            [(2,0), 0, 0, 0, 0],
            [(3,0), 0, 0, 0, 0]
        ]
        # comparing np arrays is a bit tricky 
        comparison = distance_matrix == dist.distance_matrix
        self.assertEqual(comparison.all(), True)
        # now this can be done normally
        self.assertEqual(backtrace_array, dist.backtrace_array)

    # def test_check_all_backtrace_paths_are_lists(self):
    #     dist = distances.distance('the red cat', 'the rad')
    #     dist.generate_matrixes()
    #     dist.check_all_backtrace_paths_are_lists()
    #     backtrace_array = [
    #         [0, [(0, 0)], [(0, 1)], [(0, 2)]],
    #         [[(0, 0)], [0], [0], [0]],
    #         [[(1, 0)], [0], [0], [0]]
    #     ]
    #     self.assertEqual(backtrace_array, dist.backtrace_array)

    def test_compute_unweighed_alignment(self):
        dist = match_em.distances.distance('the red cat', 'the rad', character_distances('no'))
        dist.compute_unweighted_alignment()
        distance_matrix = np.array(
            [
                [0., 1., 2., 3.],
                [1., 0., 1., 2.],
                [2., 1., 1., 2.]
            ]
        )
        backtrace_array = [
            [0, (0, 0), (0, 1), (0, 2)],
            [(0, 0), [(0, 0)], [(1, 1)], [(1, 2)]],
            [(1, 0), [(1, 1)], [(1, 1)], [(2, 2), (1, 2)]]
        ]
        # comparing np arrays is a bit tricky 
        comparison = distance_matrix == dist.distance_matrix
        self.assertEqual(comparison.all(), True)
        # now this can be done normally
        self.assertEqual(backtrace_array, dist.backtrace_array)

    def test_get_weighted_character_editops(self):
        char_edit_ops = match_em.distances.distance('perler', 'pæler', character_distances('no')).get_weighted_character_editops() # dist.get_weighted_character_editops()
        # print(char_edit_ops)
        self.assertEqual(char_edit_ops[0], ('sub', 1, 1))
        self.assertEqual(char_edit_ops[1], ('delete', 2, 1))

if __name__ == '__main__':
    unittest.main()