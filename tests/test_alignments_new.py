import unittest
import match_em.alignments_new as alignments

class AlignmentsNewTests(unittest.TestCase):
    
    def test_change_tuples_update_minus_1(self):
        change_tuples = [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 6), ('forløses', 'løse', 7), ('ei', 'seg', 8), ('lita', 'lite', 9), (' ', 'av', 10), ('jente', 'jenter', 11), ('nødkeisersnitt', 'nødkaisersnitt', 13)]
        res = alignments.update_change_tuples(
            change_tuples,
            5
        )
        self.assertEqual(
            [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 5), ('forløses', 'løse', 6), ('ei', 'seg', 7), ('lita', 'lite', 8), (' ', 'av', 9), ('jente', 'jenter', 10), ('nødkeisersnitt', 'nødkaisersnitt', 12)],
            res
        )

    def test_change_tuples_update_plus_1(self):
        change_tuples = [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 6), ('forløses', 'løse', 7), ('ei', 'seg', 8), ('lita', 'lite', 9), (' ', 'av', 10), ('jente', 'jenter', 11), ('nødkeisersnitt', 'nødkaisersnitt', 13)]
        res = alignments.update_change_tuples(
            change_tuples,
            5,
            1
        )
        self.assertEqual(
            [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 7), ('forløses', 'løse', 8), ('ei', 'seg', 9), ('lita', 'lite', 10), (' ', 'av', 11), ('jente', 'jenter', 12), ('nødkeisersnitt', 'nødkaisersnitt', 14)],
            res
        )

    def test_del_ins_series(self):
        ref = ['this', 'is', ' ', 'test']
        hyp = ['this', ' ' , 'a', 'test']
        change_tuples = [('is', ' ', 1), (' ', 'a', 2)]
        new_ref, new_hyp, new_changes = alignments.fix_del_ins_series(ref, hyp, change_tuples)
        self.assertEqual(
            new_ref,
            ['this', 'is', 'test']
        )
        self.assertEqual(
            new_hyp,
            ['this', 'a', 'test']
        )
        self.assertEqual(
            new_changes,
            [('is', 'a', 1)]
        )

    def test_ins_del_series(self):
        ref = ['this', ' ' , 'a', 'test']
        hyp = ['this', 'is', ' ', 'test']
        change_tuples = [(' ', 'is', 1), ('a', ' ', 2)]
        new_ref, new_hyp, new_changes = alignments.fix_del_ins_series(ref, hyp, change_tuples)
        self.assertEqual(
            new_ref,
            ['this', 'a', 'test']
        )
        self.assertEqual(
            new_hyp,
            ['this', 'is', 'test']
        )
        self.assertEqual(
            new_changes,
            [('a', 'is', 1)]
        )

    def test_del_ins_series_multi(self):
        ref = ['this', 'is', ' ', 'test', 'of', ' '  , 'nice', 'system']
        hyp = ['this', ' ' , 'a', 'test', 'of', 'the', ' '  , 'system']
        change_tuples = [('is', ' ', 1), (' ', 'a', 2), (' ', 'the', 5), ('nice', ' ', 6)]
        new_ref, new_hyp, new_changes = alignments.fix_del_ins_series(ref, hyp, change_tuples)
        self.assertEqual(
            new_ref,
            ['this', 'is', 'test', 'of', 'nice', 'system']
        )
        self.assertEqual(
            new_hyp,
            ['this', 'a', 'test', 'of', 'the', 'system']
        )
        self.assertEqual(
            new_changes,
            [('is', 'a', 1), ('nice', 'the', 4)]
        )

    def test_remove_spaces(self):
        self.assertEqual(
            'yehaw',
            alignments.remove_spaces('ye haw  ')
        )

    def test_shift_left_ref(self):
        res_tokens, change_tups, shifting = alignments.shift_left(
            [
                ['she', 'carried', 'a', 'heavy', 'back'    , 'pack'],
                ['she', 'carried', 'a', 'heavy', 'backpack', ' '   ],
            ],
            [('back', 'backpack', 4), ('pack', ' ', 5)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4)]
        )

    def test_shift_left_ref_eee(self):
        res_tokens, change_tups, shifting = alignments.shift_left(
            [
                ['she', 'carried', 'a', 'heavy', 'back'    , 'pack'],
                ['she', 'carried', 'a', 'heavy', 'backpack', 'eee' ],
            ],
            [('back', 'backpack', 4), ('pack', 'eee', 5)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack', ' ']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'eee']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4), (' ', 'eee', 5)]
        )

    def test_shift_left_ref_multi(self):
        res_tokens, change_tups, shifting = alignments.shift_left(
            [
                ['she', 'carried', 'a', 'heavy', 'back'    , 'pack', 'and', 'a', 'white'     , 'board'],
                ['she', 'carried', 'a', 'heavy', 'backpack', ' '   , 'and', 'a', 'whiteboard', ' '    ],
            ],
            [('back', 'backpack', 4), ('pack', ' ', 5), ('white', 'whiteboard', 8), ('board', ' ', 9)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', 'white board']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'whiteboard']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4), ('white board', 'whiteboard', 7)]
        )

    def test_shift_left_hyp(self):
        res_tokens, change_tups, shifting = alignments.shift_left(
            [
                ['she', 'carried', 'a', 'heavy', 'backpack', ' '   ],
                ['she', 'carried', 'a', 'heavy', 'back'    , 'pack']
            ],
            [('backpack', 'back',  4), (' ', 'pack',  5)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'backpack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'back pack']
        )
        self.assertEqual(
            change_tups,
            [('backpack', 'back pack', 4)]
        )

    def test_shift_left_hyp_multi(self):
        res_tokens, change_tups, shifting = alignments.shift_left(
            [
                ['she', 'carried', 'a', 'heavy', 'backpack', ' '   , 'and', 'a', 'whiteboard', ' '    ],
                ['she', 'carried', 'a', 'heavy', 'back'    , 'pack', 'and', 'a', 'white'     , 'board'],
            ],
            [('backpack', 'back',  4), (' ', 'pack',  5), ('whiteboard', 'white', 8), (' ', 'board', 9)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'whiteboard']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', 'white board']
        )
        self.assertEqual(
            change_tups,
            [('backpack', 'back pack', 4), ('whiteboard', 'white board', 7)]
        )

    ################ SHIFT RIGHT ###############################
    def test_shift_right_ref(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    ],
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack'],
            ],
            [('back', ' ', 4), ('pack', 'backpack', 5)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4)]
        )

    def test_shift_right_ref_eee(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    ],
                ['she', 'carried', 'a', 'heavy', 'eee' , 'backpack'],
            ],
            [('back', 'eee', 4), ('pack', 'backpack', 5)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', ' ', 'back pack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'eee', 'backpack']
        )
        self.assertEqual(
            change_tups,
            [(' ', 'eee', 4), ('back pack', 'backpack', 5)]
        )

    def test_shift_right_ref_multi(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    , 'and', 'a', 'white', 'board'],
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack', 'and', 'a', ' '    , 'whiteboard'],
            ],
            [('back', ' ', 4), ('pack', 'backpack', 5), ('white', ' ', 8), ('board', 'whiteboard', 9)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', 'white board']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'whiteboard']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4), ('white board', 'whiteboard', 7)]
        )
    
    def test_shift_right_ref_multi_eee(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    , 'and', 'a', 'white', 'board'],
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack', 'and', 'a', 'eee'  , 'whiteboard'],
            ],
            [('back', ' ', 4), ('pack', 'backpack', 5), ('white', 'eee', 8), ('board', 'whiteboard', 9)],
            'ref'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', ' ', 'white board']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'eee', 'whiteboard']
        )
        self.assertEqual(
            change_tups,
            [('back pack', 'backpack', 4), (' ', 'eee', 7), ('white board', 'whiteboard', 8)]
        )

    def test_shift_right_hyp(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack'],
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    ]
            ],
            [(' ', 'back',  4), ('backpack', 'pack',  5)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'backpack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'back pack']
        )
        self.assertEqual(
            change_tups,
            [('backpack', 'back pack', 4)]
        )

    def test_shift_right_hyp_eee(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', 'eee' , 'backpack'],
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    ]
            ],
            [('eee', 'back',  4), ('backpack', 'pack',  5)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'eee', 'backpack']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', ' ',   'back pack']
        )
        self.assertEqual(
            change_tups,
            [('eee', ' ', 4), ('backpack', 'back pack', 5)]
        )

    def test_shift_right_hyp_multi(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack', 'and', 'a', ' '    , 'whiteboard'],
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    , 'and', 'a', 'white', 'board'     ],
            ],
            [(' ', 'back',  4), ('backpack', 'pack',  5), (' ', 'white', 8), ('whiteboard', 'board', 9)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'whiteboard']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', 'white board']
        )
        self.assertEqual(
            change_tups,
            [('backpack', 'back pack', 4), ('whiteboard', 'white board', 7)]
        )

    def test_shift_right_hyp_multi_eee(self):
        res_tokens, change_tups, shifting = alignments.shift_right(
            [
                ['she', 'carried', 'a', 'heavy', ' '   , 'backpack', 'and', 'a', 'eee'  , 'whiteboard'],
                ['she', 'carried', 'a', 'heavy', 'back', 'pack'    , 'and', 'a', 'white', 'board'     ],
            ],
            [(' ', 'back',  4), ('backpack', 'pack',  5), ('eee', 'white', 8), ('whiteboard', 'board', 9)],
            'hyp'
        )
        self.assertEqual(
            res_tokens[0],
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'eee', 'whiteboard']
        )
        self.assertEqual(
            res_tokens[1],
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', ' ', 'white board']
        )
        self.assertEqual(
            change_tups,
            [('backpack', 'back pack', 4), ('eee', ' ', 7), ('whiteboard', 'white board', 8)]
        )

    def test_check_word_compounding(self):
        ref, hyp, change_tuples, _, created_count, broken_count, created_joins, broken_joins = alignments.check_word_compounding(
            ['she', 'carried', 'a', 'heavy', 'backpack', ' '   , 'and', 'a', 'eee'  , 'whiteboard'],
            ['she', 'carried', 'a', 'heavy', 'back'    , 'pack', 'and', 'a', 'white', 'board'     ],
            [('backpack', 'back',  4), (' ', 'pack',  5), ('eee', 'white', 8), ('whiteboard', 'board', 9)],
        )
        self.assertEqual(
            ref,
            ['she', 'carried', 'a', 'heavy', 'backpack', 'and', 'a', 'eee', 'whiteboard']
        )
        self.assertEqual(
            hyp,
            ['she', 'carried', 'a', 'heavy', 'back pack', 'and', 'a', ' ', 'white board']
        )
        self.assertEqual(
            change_tuples,
            [('backpack', 'back pack', 4), ('eee', ' ', 7), ('whiteboard', 'white board', 8)]
        )

    def test_count_compounds(self):
        created_count, broken_count, created_joins, broken_joins = alignments.count_compounds_created_broken(
            [
                ('to tusen og ti', 'totusenogti', 3),
                ('forløses', 'for løse', 4), 
                ('ei', 'seg', 5), 
                ('lita', 'lite', 6), 
                (' ', 'av', 7), 
                ('jente', 'jenter', 8), 
                ('nødkeisersnitt', 'nødkaisersnitt', 10)
            ]
        )
        self.assertEqual(
            1,
            created_count
        )
        self.assertEqual(
            1,
            broken_count
        )
        self.assertEqual(
            3,
            created_joins
        )
        self.assertEqual(
            1,
            broken_joins
        )

    def test_check_word_compounding_realEx_1(self):
        change_tuples = [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 6), ('forløses', 'løse', 7), ('ei', 'seg', 8), ('lita', 'lite', 9), (' ', 'av', 10), ('jente', 'jenter', 11), ('nødkeisersnitt', 'nødkaisersnitt', 13)]
        ref = ['fredag', 'tjuefjerde', 'september', 'to', 'tusen',       'og',  'ti', 'forløses', 'ei', 'lita',  ' ', 'jente', 'ved', 'nødkeisersnitt']
        hyp = ['fredag', 'tjuefjerde', 'september', ' ',  'totusenogti', 'for', ' ',    'løse',   'seg', 'lite', 'av', 'jenter', 'ved', 'nødkaisersnitt']
        ref, hyp, change_tuples, _, created_count, broken_count, created_joins, broken_joins = alignments.check_word_compounding(
            ref,
            hyp,
            change_tuples
        )
        self.assertEqual(
            ref,
            ['fredag', 'tjuefjerde', 'september', 'to tusen og ti', 'forløses', 'ei',  'lita',  ' ', 'jente', 'ved', 'nødkeisersnitt']
        )
        self.assertEqual(
            hyp,
            ['fredag', 'tjuefjerde', 'september', 'totusenogti',     'for løse', 'seg', 'lite', 'av', 'jenter', 'ved', 'nødkaisersnitt']
        )
        self.assertEqual(
            change_tuples,
            [
                ('to tusen og ti', 'totusenogti', 3),
                ('forløses', 'for løse', 4), 
                ('ei', 'seg', 5), 
                ('lita', 'lite', 6), 
                (' ', 'av', 7), 
                ('jente', 'jenter', 8), 
                ('nødkeisersnitt', 'nødkaisersnitt', 10)
            ]
        )
        self.assertEqual(
            1,
            created_count
        )
        self.assertEqual(
            1,
            broken_count
        )
        self.assertEqual(
            3,
            created_joins
        )
        self.assertEqual(
            1,
            broken_joins
        )

    def test_check_word_compounding_realEx_2(self):
        change_tuples = [('daihatsu', 'da', 0), ('høynet', 'hatsu', 1), ('sin', 'høynetsinguiding', 2), ('guiding', ' ', 3)]
        ref = ['daihatsu', 'høynet', 'sin', 'guiding', 'onsdag']
        hyp = ['da', 'hatsu', 'høynetsinguiding', ' ', 'onsdag']
        ref, hyp, change_tuples, _, created_count, broken_count, created_joins, broken_joins = alignments.check_word_compounding(
            ref,
            hyp,
            change_tuples
        )
        self.assertEqual(
            ref,
            ['daihatsu', 'høynet sin guiding', 'onsdag']
        )
        self.assertEqual(
            hyp,
            ['da hatsu', 'høynetsinguiding', 'onsdag']
        )
        self.assertEqual(
            change_tuples,
            [
                ('daihatsu', 'da hatsu', 0),
                ('høynet sin guiding', 'høynetsinguiding', 1), 
            ]
        )
        self.assertEqual(
            1,
            created_count
        )
        self.assertEqual(
            1,
            broken_count
        )
        self.assertEqual(
            2,
            created_joins
        )
        self.assertEqual(
            1,
            broken_joins
        )
        
if __name__ == '__main__':
    unittest.main()