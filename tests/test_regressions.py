import unittest

from match_em import analysis

'''
These are the tests that orignally lived in teh the wav2vec_wer_tester.ipynb file.
They are NOT unit tests persay, rather they're regression tests with expected results
'''

class AlignmentsTests(unittest.TestCase):

    def test_regression_1(self):
        results = analysis.compute_mistakes('frå neste veke av vart altså', 'fra neste veka var altså')
        self.assertTrue(final_prints_the_same(expected_prints[1], results['final_print']))  

    def test_regression_2(self):
        results = analysis.compute_mistakes('frå neste veke av vart altså', 'fra neste veka var altså', distance_method='weighted_manual')
        self.assertTrue(final_prints_the_same(expected_prints[2], results['final_print'])) 

    def test_regresstion_3(self):
        ref = 'men etter hvert så ble jeg vant lig det og ble vant til å være sammen med dyra nedi laben der og det var egentlig ganske trivelig'
        hyp = 'men eee etter hvert så ble det vanlig og ble vant til å være samme dyra ned i laben er og det var egentlig ganske trivelig'
        results = analysis.compute_mistakes(ref, hyp, distance_method='weighted_manual')
        self.assertEqual(results['compounds_created'], 1)
        self.assertEqual(results['compounds_deleted'], 1)
        self.assertTrue(final_prints_the_same(expected_prints[3], results['final_print'])) 

    def test_regression_4(self):
        ref = 'da ble det nemlig slik at de spilte en en hjemme første kampen og så ble det to to da på ullevål'
        hyp = 'da var nemisikke spilt en ein heime i første kampen og så ble det to torer på ulleval'
        # specifically this is testing python-Levenshtein get_alignment_word() aka Issue 1
        results = analysis.compute_mistakes(ref, hyp)
        self.assertTrue(final_prints_the_same(expected_prints[4], results['final_print'])) 

    def test_regression_5(self):
        ref = "DAIHATSU HøYNET SIN GUIDING onsdag".lower()
        hyp = 'DA HATSU HøYNETSINGUIDING onsdag'.lower()
        utt_id = ['p1_g01_f1_2_b0065']
        results = analysis.compute_mistakes(
            ref, 
            hyp, 
            utt_id, 
            distance_method='weighted_manual'
        )
        self.assertTrue(final_prints_the_same(expected_prints[5], results['final_print'])) 

    def test_regression_6(self):
        ref = 'come flexbox e animazioni css'
        hyp = 'meflex box e animazioni ci è sterse'
        results = analysis.compute_mistakes(
            ref, 
            hyp, 
            distance_method='weighted_manual',
            allow_greater_than_1_sub_cost=True,
            language='it'
        )
        self.assertTrue(final_prints_the_same(expected_prints[6], results['final_print'])) 


expected_prints = {
    1: '''--- UNK_ID (WER: 60.0, compounds created: 1, compounds broken up: 0)---
  f | r | å    ||  neste  ||   v | e | k | e |   | a | v    ||   v | a | r | t    ||  altså  || 
  f | r | a    ||  neste  ||   v | e | k |   |   | a |      ||   v | a | r |      ||  altså  || 
    |   | S    ||         ||     |   |   | D | D |   | D    ||     |   |   | D    ||         || 
    ''',
    2: '''--- UNK_ID (WER: 66.67, compounds created: 0, compounds broken up: 0)---
  f | r | å    ||  neste  ||   v | e | k | e    ||   a | v    ||   v | a | r | t    ||  altså  || 
  f | r | a    ||  neste  ||   v | e | k | a    ||     |      ||   v | a | r |      ||  altså  || 
    |   | S    ||         ||     |   |   | S    ||   D | D    ||     |   |   | D    ||         || 
    ''',
    3: '--- UNK_ID (WER: 29.63, compounds created: 1, compounds broken up: 1)---\n men  ||     |   |      ||  etter  ||  hvert  ||  så  ||  ble  ||   j | e | g    ||   v | a | n | t |   | l | i | g    ||   d | e | t    ||  og  ||  ble  ||  vant  ||  til  ||  å  ||  være  ||   s | a | m | m | e | n    ||   m | e | d    ||  dyra  ||   n | e | d |   | i    ||  laben  ||   d | e | r    ||  og  ||  det  ||  var  ||  egentlig  ||  ganske  ||  trivelig  || \n men  ||   e | e | e    ||  etter  ||  hvert  ||  så  ||  ble  ||   d | e | t    ||   v | a | n |   |   | l | i | g    ||     |   |      ||  og  ||  ble  ||  vant  ||  til  ||  å  ||  være  ||   s | a | m | m | e |      ||     |   |      ||  dyra  ||   n | e | d |   | i    ||  laben  ||     | e | r    ||  og  ||  det  ||  var  ||  egentlig  ||  ganske  ||  trivelig  || \n      ||   I | I | I    ||         ||         ||      ||       ||   S |   | S    ||     |   |   | D | D |   |   |      ||   D | D | D    ||      ||       ||        ||       ||     ||        ||     |   |   |   |   | D    ||   D | D | D    ||        ||     |   |   | I |      ||         ||   D |   |      ||      ||       ||       ||            ||          ||            || \n\n',
    4: '''
--- UNK_ID (WER: 54.55, compounds created: 1, compounds broken up: 0)---
 da  ||   b | l | e    ||   d | e | t    ||   n | e | m | l | i | g    ||   s | l | i | k    ||   a | t |   | d | e |   |   |   | s | p | i | l | t | e    ||     |   |   |   |      ||  en  ||   e |   | n    ||   h | j | e | m | m | e    ||        ||  første  ||  kampen  ||  og  ||  så  ||  ble  ||  det  ||   t | o    ||  to  ||   d | a |   |   |      ||  på  ||   u | l | l | e | v | å | l    || 
 da  ||     |   |      ||     |   |      ||     |   |   |   |   |      ||   v |   | a | r    ||     | n | e | m | i |   |   |   | s |   | i | k | k | e    ||   s | p | i | l | t    ||  en  ||   e | i | n    ||   h |   | e | i | m | e    ||   i    ||  første  ||  kampen  ||  og  ||  så  ||  ble  ||  det  ||     |      ||  to  ||   t | o | r | e | r    ||  på  ||   u | l | l | e | v | a | l    || 
     ||   D | D | D    ||   D | D | D    ||   D | D | D | D | D | D    ||   S | D | S | S    ||   D | S | S | S | S | D | D | D |   | D |   | S | S |      ||   I | I | I | I | I    ||      ||     | I |      ||     | D |   | S |   |      ||   I    ||          ||          ||      ||      ||       ||       ||   D | D    ||      ||   S | S | I | I | I    ||      ||     |   |   |   |   | S |      || 
''',
    5: '''
    --- p1_g01_f1_2_b0065 (WER: 66.67, compounds created: 1, compounds broken up: 1)---
  d | a | i | h | a | t | s | u    ||   h | ø | y | n | e | t |   | s | i | n |   | g | u | i | d | i | n | g    ||  onsdag  || 
  d | a |   | h | a | t | s | u    ||   h | ø | y | n | e | t |   | s | i | n |   | g | u | i | d | i | n | g    ||  onsdag  || 
    |   | S |   |   |   |   |      ||     |   |   |   |   |   | D |   |   |   | D |   |   |   |   |   |   |      ||          || 
''',
    6:'''
--- UNK_ID (WER: 71.43, compounds created: 0, compounds broken up: 1)---
  c | o | m | e    ||     |   | f | l | e | x |   | b | o | x    ||  e  ||  animazioni  ||     |      ||        ||     | c |   | s | s |      || 
    |   |   |      ||   m | e | f | l | e | x |   | b | o | x    ||  e  ||  animazioni  ||   c | i    ||   è    ||   s | t | e | r | s | e    || 
  D | D | D | D    ||   I | I |   |   |   |   | I |   |   |      ||     ||              ||   I | I    ||   I    ||   I | S | I | S |   | I    ||
'''
}

def final_prints_the_same(truth, test_result):
    truth_lines = [l.strip() for l in truth.split('\n') if l.strip() != '']
    test_lines = [l.strip() for l in test_result.split('\n') if l.strip() != '']

    if truth_lines != test_lines:
        for i in range(len(truth_lines)):
            if truth_lines[i] != test_lines[i]:
                print("This one (test)->{}<-".format(test_lines[i]))
                print('v.s. (truth)->{}<-'.format(truth_lines[i]))
        import os
        debug_temp = '/localhome/stipendiater/plparson/match-em/tests/debug_temp.txt'
        open_method = 'w'
        if os.path.isfile(debug_temp):
            open_method = 'a'
        with open(debug_temp, open_method) as open_f:
            open_f.write('-----------Test Boundary----------------')
            open_f.write(truth)
            open_f.write(test_result)
            open_f.write('\n')

    return(truth_lines == test_lines)

if __name__ == '__main__':
    unittest.main()