import unittest
import match_em.alignments as alignments

class AlignmentsTests(unittest.TestCase):
    
    def test_compounding_one(self):
        ref = 'fredag tjuefjerde september to tusen og ti forløses ei lita jente ved nødkeisersnitt'
        hyp = 'fredag tjuefjerde september totusenogti for løse seg lite av jenter ved nødkaisersnitt'
        # dist = distance(ref, hyp)
        # computed_editops = dist.get_weighted_editops(allow_greater_than_1=True)
        editops = [('delete', 3, 2), ('sub', 4, 3), ('sub', 5, 4), ('delete', 6, 4), ('sub', 7, 5), ('sub', 8, 6), ('sub', 9, 7), ('insert', 9, 8), ('sub', 10, 9), ('sub', 12, 11)]
        # changes_tuples, index_changes, ref, hyp = get_alignment_words(ref, hyp, computed_editops)
        change_tuples = [('to', ' ', 3), ('tusen', 'totusenogti', 4), ('og', 'for', 5), ('ti', ' ', 6), ('forløses', 'løse', 7), ('ei', 'seg', 8), ('lita', 'lite', 9), (' ', 'av', 10), ('jente', 'jenter', 11), ('nødkeisersnitt', 'nødkaisersnitt', 13)]
        index_changes = {3: ' ', 4: 'S', 5: 'S', 6: ' ', 7: 'S', 8: 'S', 9: 'S', 10: ' ', 11: 'S', 13: 'S'}
        ref = ['fredag', 'tjuefjerde', 'september', 'to', 'tusen',       'og',  'ti', 'forløses', 'ei', 'lita',  ' ', 'jente', 'ved', 'nødkeisersnitt']
        hyp = ['fredag', 'tjuefjerde', 'september', ' ',  'totusenogti', 'for', ' ',    'løse',   'seg', 'lite', 'av', 'jenter', 'ved', 'nødkaisersnitt']
        # changes_tuples, index_changes, ref, hyp, created_compound, brokeup_compound = check_word_compounding(changes_tuples, index_changes, ref, hyp)
        change_tuples = [('tusen', 'totusenogti', 3), ('og', 'for', 4), ('ti', ' ', 5), ('forløses', 'løse', 6), ('ei', 'seg', 7), ('lita', 'lite', 8), (' ', 'av', 9), ('jente', 'jenter', 10), ('nødkeisersnitt', 'nødkaisersnitt', 12)]
        index_changes = {3: 'S', 4: 'S', 5: ' ', 6: 'S', 7: 'S', 8: 'S', 9: ' ', 10: 'S', 12: 'S'}
        ref = ['fredag', 'tjuefjerde', 'september', 'to tusen',    'og', 'ti', 'forløses', 'ei', 'lita', ' ', 'jente', 'ved', 'nødkeisersnitt']
        hyp = ['fredag', 'tjuefjerde', 'september', 'totusenogti', 'for', ' ',  'løse', '  seg', 'lite', 'av', 'jenter', 'ved', 'nødkaisersnitt']
        created_compound = 1
        brokeup_compound = 0

if __name__ == '__main__':
    unittest.main()