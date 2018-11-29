import unittest

import pandas as pd

from scopuspep.scopuspep import Scopuspep


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.spep = Scopuspep()


    def tearDown(self):
        del self.spep

    
    def test_main_author(self):
        spep = Scopuspep()        

        authors = 'Author 1, Author 2, Author 3, Author 4'
        main_author = 'Author 1'
        self.assertEqual(main_author, spep.main_author(authors))

        authors = 'Author X Y'
        main_author = 'Author X Y'
        self.assertEqual(main_author, spep.main_author(authors))


    def test_format_author_year(self):
        spep = Scopuspep()

        authors = 'Foo Xu, Bar Li, Zen Fu'
        year =  2015
        result = spep.format_author_year(authors, year)
        expected = 'Foo Xu, Bar Li, Zen Fu (2015)'

        authors = 'Yoo Zu'
        year =  2013
        result = spep.format_author_year(authors, year)
        expected = 'Yoo Zu (2013)'
    
        self.assertEqual(expected, result)        


    def test_author_et_al(self):
        spep = Scopuspep()

        authors = 'Pedro'
        result = spep.author_et_al(authors)
        expected = 'Pedro'
        self.assertEqual(expected, result)

        authors = 'Zu, Wui, Sousa'            
        result = spep.author_et_al(authors)
        expected = 'Zu, Wui, Sousa' 
        self.assertEqual(expected, result)
                
        authors = 'Xu, Li, Fu, Xi'
        result = spep.author_et_al(authors)
        expected = 'Xu et al' 
        self.assertEqual(expected, result)
        #self.assertEqual()
    
    def test_process_dataframe(self):
        """

        Be careful of use None in the test, for example in the cited by key
        if it has some NaN values and it is represented as np.nan the test will
        fail because np.nan == np.nan returns false.

        https://stackoverflow.com/a/44367571
        https://stackoverflow.com/questions/50797375/python-unittest-assert-complex-dictionary
        """        
        spep = Scopuspep()                  

        d = {'Authors':['Chen J., Xiong F., Zheng J., Ge Q., Cheng F.', 
                'Briggs M.A., Buckley S.F., Bagtzoglou A.C.',
                'Banks E.W., Shanafield M.A., Cook P.G.'],
                'Cited by':[10, 11.0, 14.0],
                'Year':[2011, 2012, 2013],
                }

        expected = {'Authors': {0: 'Chen J., Xiong F., Zheng J., Ge Q., Cheng F.', 
                                                 1: 'Briggs M.A., Buckley S.F., Bagtzoglou A.C.',
                                                 2: 'Banks E.W., Shanafield M.A., Cook P.G.'}, 
                             'Cited by': {0: 10.0, 1: 11.0, 2: 14.0}, 
                             'Year': {0: 2011, 1: 2012, 2: 2013}, 
                             'Authors_et_al': {0: 'Chen J. et al', 
                                                           1: 'Briggs M.A., Buckley S.F., Bagtzoglou A.C.',
                                                           2: 'Banks E.W., Shanafield M.A., Cook P.G.'},
                             'main_author': {0: 'Chen J.', 1: 'Briggs M.A.', 2: 'Banks E.W.'}, 
                             'Authors_et_al_years': {0: 'Chen J. et al (2011)',
                                                                     1: 'Briggs M.A., Buckley S.F., Bagtzoglou A.C. (2012)', 
                                                                     2: 'Banks E.W., Shanafield M.A., Cook P.G. (2013)'}, 
                            'main_author_year': {0: 'Chen J. (2011)', 
                                                                 1: 'Briggs M.A. (2012)', 
                                                                 2: 'Banks E.W. (2013)'}, 
                            'Cited_by_count': {0: 10.0, 1: 11.0, 2: 14.0}, 
                            'Label': {0: 'Chen J. et al (2011)', 
                                           1: 'Briggs M.A., Buckley S.F., Bagtzoglou A.C. (2012)', 
                                           2: 'Banks E.W., Shanafield M.A., Cook P.G. (2013)'}, 
                            'id': {0: 0, 1: 1, 2: 2}}


        df  = pd.DataFrame(d)
        result = spep.process_dataframe(df).to_dict()
        #self.maxDiff = None
        self.assertDictEqual(expected, result)

    def test_build_EIDs_dict(self):
        # TODO: use mock to test this
        pass

    def test_EIDs_list(self):
        spep = Scopuspep()

        expected = ['2-s2.0-84927548524',
                            '2-s2.0-84934272588',
                            '2-s2.0-84928807095']

        d = {'EID': expected}

        df  = pd.DataFrame(d)

        result = spep.EIDs_list(df)

        self.assertEqual(expected, result)

    
    def test_build_edges(self):
        """
        
        EIDs: is a list of eids of the "base" articles that is going to constructed 
        the net.
        EIDs_dict: is a dictionary where keys are the eids from EIDs, and the 
        values o each key are the references of each base article.        
        """
        spep = Scopuspep()

        EIDs = ['2-s2.0-85052823139',
                  '2-s2.0-84978115007',
                  '2-s2.0-84902375090']

        EIDs_dict = {'2-s2.0-85052823139': ['2-s2.0-84978115007',
                                                                    '2-s2.0-0036695720',
                                                                    '2-s2.0-0036609180',
                                                                    '2-s2.0-85007060782'],
                            '2-s2.0-84978115007': ['2-s2.0-85052823139',
                                                                      '2-s2.0-79952750687'],
                            '2-s2.0-84902375090': ['2-s2.0-84902375090',                                                                    
                                                                      '2-s2.0-84861539763',
                                                                      '2-s2.0-33846212765']
                        }

        # Why the .to_dict() return a dict in this format?
        expected = {'Source': {0: 1, 1: 0, 2: 2}, 'Target': {0: 0, 1: 1, 2: 2}}
        result = spep.build_edges(EIDs, EIDs_dict).to_dict()
        #print(result)
        self.assertEqual(expected, result)

    def test_reindex_data_frame(self):

        spep = Scopuspep()

        columns = 'id Label Cited_by_count Authors_et_al_years main_author_year A B C'. split()
        
        expected = {column:{} for column in columns}

        df  = pd.DataFrame(expected)

        result = spep.reindex_data_frame(df).to_dict()
        
        self.assertEqual(expected, result)


    # Tests of main_authors

    def test_build_author_ids_EIDs_articles(self):
        """
        
        Note: The tuple has two elements that are lists
        """
        spep = Scopuspep()

        d = {'Author Ids': {0: '35307313800;8683860000;7005595203;',
                                         1: '15220062200;15220688300;57193863782;56991049200;'},
                'EID': {0: '2-s2.0-84923096575', 1: '2-s2.0-84949116368'}
                }

        expected = (['35307313800;8683860000;7005595203;',
         '15220062200;15220688300;57193863782;56991049200;'], 
         ['2-s2.0-84923096575', '2-s2.0-84949116368'])

        
        df  = pd.DataFrame(d)
        result = spep.build_author_ids_EIDs_articles(df)        

        #print(result)

        self.assertEqual(expected, result)


    def test_build_df_authors(self):
        # TODO: use mock to test this
        pass

    def test_build_set_all_authors(self):
        
        spep = Scopuspep()

        author_ids =['35307313800;8683860000;35307313800;',
                               '57193863782;56991049200;']
        
        expected = {'56991049200', '57193863782', '35307313800', '8683860000'}
        result = spep.build_set_all_authors(author_ids)        

        self.assertEqual(expected, result)


    
    def test_build_dict_author_articles(self): 
        pass


    def test_build_df_authors(self):
        pass


    def test_build_df_edges_authors_articles(self):
        # TODO: check if the doubled edge problem
        pass    

    #def test_(self):

    def test_reindex_id(self):
        
        spep = Scopuspep()
        
        columns = 'id A B C D'.split()
        expected = {column:{} for column in columns}

        df  = pd.DataFrame(expected)

        result = spep.reindex_id(df).to_dict()
        
        self.assertEqual(expected, result)
    

if __name__ == '__main__':
    unittest.main()














