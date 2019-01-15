import datetime

import numpy as np
import pandas as pd

import scopus

from collections import Counter

from scopus import ScopusAbstract
from scopus import ScopusAuthor


class Scopuspep():
	
	def __init__(self, path=None):
		"""
		
		"""
		# This is a good pattern?
		# To give flexibilite path shuld be optional??
		if path is not None:
			self.df = pd.read_csv(path)
		else:
			self.df = None
		

		self.df_edges = None


	def author_et_al(self, authors):
		"""This function formats author's name, if the number of authors is less
		than 3 it remains the same, else it gets the first author's name and adds 
		et al to it.

		The Elsevier exported file is formated in order of authors, so is possible 
		trust that the first author in the .csv file is the same one of the .pdf 
		article/paper published.
		"""

		formated_author = []
		
		s = authors.split(',')    

		if len(s) > 3:
			formated_author.append(s[0] + ' et al')
		else:
			formated_author.append(authors)
			
		return formated_author[0]


	def main_author(self, author):
		"""

		Note: The name shuld be main author or first author are the same thing.
		"""
			
		return author.split(',')[0]


	# TODO change this name?
	def format_author_year(self, authors, year):    
		"""
		"""
		return str(authors) + ' (' + str(year) + ')'


	def process_dataframe(self, df=None):
		"""
		"""

		if df is None:
			df = self.df

		df['Authors_et_al'] = df['Authors'].apply(self.author_et_al)
		df['main_author'] = df['Authors'].apply(self.main_author)

		#https://stackoverflow.com/questions/34279378/python-pandas-apply-function-with-two-arguments-to-columns
		df['Authors_et_al_years'] = df.apply(lambda x: self.format_author_year(x['Authors_et_al'], x['Year']), axis=1)
		df['main_author_year'] = df.apply(lambda x: self.format_author_year(x['main_author'], x['Year']), axis=1)

		df['Cited_by_count'] = df['Cited by']
		df['Label'] = df['Authors_et_al_years']

		df["id"] = df.index

		return df


	def EIDs_list(self, df=None):
		"""
		"""

		if df is None:
			df = self.df

		return df['EID'].tolist()


	def build_EIDs_dict(self, EIDs, refresh=False):
		"""

		"""

		EIDs_dict = {}
		for eid in EIDs:
			# TODO: migrate to new version of scopus
			# AbstractRetrieval
			ab = ScopusAbstract(eid, view='FULL', refresh=refresh)
			EIDs_dict.update({eid:ab.references})

		return EIDs_dict


	def build_edges(self, EIDs=None, EIDs_dict=None, refresh=False):
		"""
		"""

		if EIDs is None:
			EIDs = self.EIDs_list(self.df)

		if EIDs_dict is None:
			EIDs_dict = self.build_EIDs_dict(EIDs, refresh)


		dict_source_target = {'Source':[], 
											  'Target':[],
											  'source_article_eid':[],
											  'target_author_eid':[],										
											  }
			
		for i, eid in enumerate(EIDs):
			references = EIDs_dict[eid]
			for j, base_eid in enumerate(EIDs):
				if base_eid in references:
					dict_source_target['Source'].append(j)
					dict_source_target['Target'].append(i)

					dict_source_target['source_article_eid'].append(base_eid)
					dict_source_target['target_author_eid'].append(eid)
					
		df_edges = pd.DataFrame(dict_source_target)
		
		self.df_edges = df_edges

		return df_edges


	# TODO: Find a better name.
	def f_year(self, i, years):
	    return years[i]


	def delta_years(self, df_edges=None):

		if df_edges is None:
			if self.df_edges is None:
				df_edges = self.build_edges()
			else:
				df_edges = self.df_edges

		df_edges['Source_Year'] = df_edges.apply(lambda x: self.f_year(x['Source'], self.df['Year']), axis=1)
		df_edges['Target_Year'] = df_edges.apply(lambda x: self.f_year(x['Target'], self.df['Year']), axis=1)

		df_edges['delta_years'] = df_edges['Target_Year'] - df_edges['Source_Year']

		return df_edges


	#TODO: better name, just reindex?
	def reindex_data_frame(self, df=None):
		
		if df is None:
			df = self.df

		columns = df.columns.tolist()

		#TODO: Standardise columns names
		l = 'id Label Cited_by_count n_cited n_quotes Authors_et_al_years main_author_year'.split()

		ordered_columns = l + [column for column in columns if column not in l]

		df = df.reindex(columns=(ordered_columns))

		return df


	def build_nodes(self, df=None, df_edges=None):

		if df is None:
			df = self.df

		if df_edges is None:
			if self.df_edges is None:
				self.df_edges = self.build_edges()					
			else:
				df_edges = self.df_edges

		source_article_eid = df_edges['source_article_eid'].value_counts()
		target_author_eid = df_edges['target_author_eid'].value_counts()

		EIDs = self.EIDs_list(self.df)

		n_cited = [0 if eid not in source_article_eid.keys() 
							else 
							source_article_eid[eid]
							for eid in EIDs
						]

		n_quotes = [0 if eid not in target_author_eid.keys() 
								else 
								target_author_eid[eid] 
								for eid in EIDs
							]

		self.df['n_cited'] = n_cited
		self.df['n_quotes'] = n_quotes

		df = self.reindex_data_frame()

		return df


	def who_cited_who(self, df=None, refresh=False):
		"""
		
		Note: The order to build edges and nodes ara importante, because 
		if it was done in oposite way calculation would be done again unnecessarily.
		Now as the nodes utilise information from the edges data frame to calculate 
		`n_cited` and  `n_quotes` it make sense first calculate the edges daframe stuff.
		"""
		
		if df is None:
			df = self.df

		EIDs = self.EIDs_list(df)

		EIDs_dict = self.build_EIDs_dict(EIDs, refresh)

		df_edges = self.build_edges(EIDs, EIDs_dict)	
	
		df_edges = self.delta_years(df_edges)

		# nodes processing
		processed_df = self.process_dataframe(df)

		df_nodes = self.build_nodes()		

		return df_nodes, df_edges


###

	def build_author_ids_EIDs_articles(self, df_articles=None) -> tuple:
		"""This function extracts author ids and eids from a given data frame.

		returns a tuple of  two lists: author_ids, EIDs_articles
		"""
		if df_articles is None:
			df_articles = self.df
		
		author_ids = df_articles['Author Ids'].tolist()
		EIDs_articles = df_articles['EID'].tolist()
		
		return author_ids, EIDs_articles


	def build_set_all_authors(self, author_ids: list=None) -> set:
		"""Creates a set of all athors.
		
		"""

		if author_ids is None:
			author_ids, EIDs_articles = self.build_author_ids_EIDs_articles()

		return set([author for authors in author_ids for author in authors.split(';') if author != ''])


	def build_dict_author_articles(self, df_articles=None, all_authors: set=None,
														 author_ids:list=None, EIDs_articles: list=None) -> dict:
		"""Cretes a where each key is the author_id and the value is a list of articles.
		
		TODO: check if the way to do this is as it is now.
		https://stackoverflow.com/questions/43279256/multiple-optional-arguments-python
		"""

		if df_articles is None:
			df_articles = self.df

		if all_authors is None:
			all_authors = self.build_set_all_authors()

		if author_ids is None:
			author_ids, _EIDs_articles = self.build_author_ids_EIDs_articles()

		if EIDs_articles is None:
			EIDs_articles = _EIDs_articles


		dict_eids_authors = {}

		# This could be a separeted function
		for eid, authors in zip(EIDs_articles, author_ids):
			cleaned_authors = [authors for authors in authors.split(';') if authors != '']
			dict_eids_authors.update({eid:cleaned_authors})

		dict_author_articles = {}

		# This could be a separeted function
		for _ in dict_eids_authors:
			for author in all_authors:
				articles = []
				for eid_author in dict_eids_authors:
					if author in dict_eids_authors[eid_author]:
						articles.append(eid_author)
						dict_author_articles.update({author:articles})

		# If were wished to filter               
		# {key:author_articles[key] for key in author_articles if len(author_articles[key])>1}

		return dict_author_articles


	def build_df_authors(self, all_authors=None):
		"""Given all authors without repetition builds a data frame of all 
		authors and they information.
		
		TODO: document all columns of the data frame.
		"""

		if all_authors is None:
			all_authors = self.build_set_all_authors()
		
		d = {'Name':[],
			 'Number of documents':[],
			 'Number of citations':[],
			 'hindex':[],
			 'orcid':[],
			 'current_affiliation':[],
			 'author_id':[],
			 'scopus_url':[],
			 'n_first_author_papers':[],
			 'n_journal_articles':[],
			 'n_last_author_papers':[],
			 'scopus_url':[],
			 'subject_areas':[],
			 #'citations count in 2016 and 2017':[],
			 #'publication count in 2016 and 2017':[],
			 #'author impact factor 2018':[],
			 'type':[],
			}

		for author_id in all_authors:
			
			# TODO: migrate to new version
			# AuthorRetrieval
			au = ScopusAuthor(author_id)

			d['Name'].append(au.name)

			# Most important not equal to au.ndocuments, why?
			d['Number of citations'].append(au.citation_count)

			# Not all documents cited in the au.citation_count are in au.ndocuments why?
			d['Number of documents'].append(au.ndocuments)

			d['hindex'].append(au.hindex)
			d['orcid'].append(au.orcid)
			d['current_affiliation'].append(au.current_affiliation)

			d['scopus_url'].append(au.scopus_url)
			d['n_first_author_papers'].append(au.n_first_author_papers)
			d['n_journal_articles'].append(au.n_journal_articles)
			d['n_last_author_papers'].append(au.n_last_author_papers)
			d['subject_areas'].append(au.subject_areas)

			d['author_id'].append(author_id)
			d['type'].append('author')

			# It realy slows  the code.
			# https://github.com/scopus-api/scopus/blob/master/scopus/scopus_author.py#L358
			# tup = au.author_impact_factor(year=2018)

			#d['citations count in 2016 and 2017'].append(tup[0])
			#d['publication count in 2016 and 2017'].append(tup[1])
			#d['author impact factor 2018'].append(tup[2])
		
		df = pd.DataFrame(d)

		df["id"] = df.index

		return df


	def build_df_edges_authors_articles(self, dict_author_articles=None,
																						 df_articles=None):

		if dict_author_articles is None:
			dict_author_articles = self.build_dict_author_articles()

		if df_articles is None:
			df_articles = self.df
		
		# TODO: n_connected_articles does not meke sense!
		dict_source_target = {'Source':[],
											  'Target':[],
											  'article_id':[],
											  'author_id':[],
											  'year_publication':[],
											  'n_connected_articles':[],
			     							}

		article_processed = []
		ids_articles = []
		
		# TODO: check if the doubled edge problem comes to here
		cont_articles = len(dict_author_articles)  + 1 

		for i, eid in enumerate(dict_author_articles):

			for article in dict_author_articles[eid]:
				if article not in article_processed:
					article_processed.append(article)
					cont_articles += 1
					ids_articles.append(cont_articles)

				#print(i, cont_articles, eid, article)
				dict_source_target['Source'].append(i)
				dict_source_target['Target'].append(cont_articles)
				dict_source_target['article_id'].append(article)
				dict_source_target['author_id'].append(eid)
				dict_source_target['year_publication'].append(int(df_articles[df_articles['EID'] == article]['Year']))
				dict_source_target['n_connected_articles'].append(len(dict_author_articles[eid]))

		df_edges_authors_articles = pd.DataFrame(dict_source_target)
		
		now = datetime.datetime.now()
		
		df_edges_authors_articles['elapsed_time_publication'] =  now.year - df_edges_authors_articles['year_publication']

		return df_edges_authors_articles, ids_articles


	def set_id_and_type(self, df_articles=None, ids_articles=None):

		if df_articles is None:
			df_articles = self.df

		if ids_articles is None:
			df_edges_authors_articles, _ids_articles = self.build_df_edges_authors_articles()
			ids_articles = _ids_articles

		# TODO: standardise these names, plural or singular
		df_articles['id'] = ids_articles
		df_articles['type'] = 'article'

		return df_articles


	# TODO: rename and/or factor the logic of reindex
	# Really bad name
	def reindex_id_Name_Year_hindex (self, df):
		columns = df.columns.tolist()

		l = 'id Name Year hindex '.split()

		ordered_columns = l + [column for column in columns if column not in l]

		df = df.reindex(columns=(ordered_columns))
		return df


	def reindex_id(self, df):
		"""Given a data frame reindex de data frame id column fisrt.
			
		"""

		columns = 'id Label Cited_by_count Authors_et_al_years main_author_year'.split()
		cols = df.columns.tolist()

		# TODO: choose another names
		ord_cols = ['id'] + [col for col in cols if col not in columns]

		df = df.reindex(columns=(ord_cols))
		return df


	def main_authors(self, df_articles=None):
		"""
		
		Minimal columns to this work?
		"""
		if df_articles is None:
			df_articles = self.df

		author_ids, EIDs_articles = self.build_author_ids_EIDs_articles(df_articles)

		all_authors = self.build_set_all_authors(author_ids)

		dict_author_articles = self.build_dict_author_articles(df_articles,
		 												all_authors, author_ids, EIDs_articles)

		df_authors = self.build_df_authors(all_authors)


		df_edges_authors_articles, ids_articles = self.build_df_edges_authors_articles(
																	dict_author_articles, df_articles)

		df_articles = self.set_id_and_type(df_articles, ids_articles)

		df_node_authors_articles = pd.concat([df_authors, df_articles], 
																		ignore_index=True, sort=False)

		df_node_authors_articles = self.reindex_id_Name_Year_hindex(
																				df_node_authors_articles)

		return df_node_authors_articles, df_edges_authors_articles


	def key_words_count(self, df=None):

		if df is None:
			df = self.df

		df = df[df['Author Keywords'].notnull()]
		article_key_words = df['Author Keywords'].tolist()
		
		words = [key_word for key_words in article_key_words for key_word in key_words.split('; ')]

		s = pd.Series(words)
		s = s.value_counts()
		return s

	def cocited_rank(self, n, EIDs=None, EIDs_dict=None):
		"""

		"""
		
		if EIDs is None:	
			EIDs = self.EIDs_list()

		if EIDs_dict is None:	
			EIDs_dict = spep.build_EIDs_dict(EIDs)

		EIDs_repeated = [eid for key in EIDs_dict for eid in EIDs_dict[key]]

		# This removes the base articles from the references
		EIDs_repeated = [key for key in EIDs_repeated if key not in EIDs]

		couted_EIDs = Counter(EIDs_repeated)
		couted_EIDs = couted_EIDs.most_common(n)

		d = {'scopus_url':[],
		    'eid':[],
		    'title':[],
		    'doi':[],
		    }

		for eid in couted_EIDs:
		    ab = ScopusAbstract(eid[0], view='FULL')
		    d['scopus_url'].append(ab.scopus_url)
		    d['eid'].append(ab.eid)
		    d['title'].append(ab.title)
		    d['doi'].append(ab.doi)

		df = pd.DataFrame(d)

		return df