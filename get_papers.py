import os
from time import sleep
from csv import DictWriter, writer
import re

from habanero import Crossref  # CrossRef API access

HABANERO_USERNAME = ""  # provide an email address so they can contact you if your script misbehaves
ISSN = ""  # ISSN of the journal to dump data for
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
SLEEP_TIME = 0.05  # sleep for 50 ms between requests to be nice to the CrossRef API
PER_PAGE = 1000  # How many items to download at once. 1000 is current max in API, lowering it will take longer, but could be desirable.
KEYS_TO_KEEP = [u'DOI', u'issued', u'prefix', u'relation', u'author', u'reference-count', u'ISSN', u'member', u'source', u'score', u'deposited', u'indexed', u'type', u'published-online', u'URL', u'is-referenced-by-count', u'volume', u'issn-type', u'link', u'published-print', u'journal-issue', u'references-count', u'short-container-title', u'publisher', u'content-domain', u'language', u'license', u'created', u'issue', u'title', u'alternative-id', u'container-title', u'page']  # which items should we dump to our spreadsheets? - can also add u'reference', but it can break CSV outputs

def make_data_safe(paper, keys=KEYS_TO_KEEP):
	"""
		Originally handled converting to string, but abandoned that for now so we can do some other analysis below.
		Now just saves the parts we actually want to keep, does nothing else. Could be skippable, but the DictWriter
		might complain
	"""
	output_dict = {}
	for key in keys:
		if key in paper:
			output_dict[key] = paper[key] 
	
	return output_dict

def _combine_dict_to_list(frequencies):
	item_frequencies = []  # make a list instead of a dict
	for item in frequencies:
		item_frequencies.append([item, frequencies[item]])  # make it a list of lists so we can write it out with a listwriter
		
	return item_frequencies
	
def frequency_titles(papers):
	print("Getting frequency of words in titles")
	words = {}
	for paper in papers:
		title = paper['title'][0].encode('utf-8')
		title_words = re.findall("\w+", title)
		for word in title_words:
			match_word = word.lower()
			if len(match_word) > 2:
				if match_word not in words:
					words[match_word] = 1  # initialize it if it's not there yet
				else:
					words[match_word] += 1  # otherwise increment its frequency
				
	return _combine_dict_to_list(words)
	
def frequency_institutions(papers):
	print("Getting frequency of institutions")
	institutions = {}
	
	for paper in papers:
		if not "author" in paper:
			continue
		
		for author in paper["author"]:
			for affiliation in author["affiliation"]:
				affiliation_lower = affiliation['name'].lower().encode('utf-8')
				affiliation_parts = affiliation_lower.split(",")
				for part in affiliation_parts:  # try to figure out what their actual university is, not their institute, school, center, department, etc
					if "university" in part:
						affiliation_lower = part
						
				if affiliation_lower.startswith(" "):
					affiliation_lower = affiliation_lower.replace(" ", "", 1)  # if it starts with a space, remove the first space
						
				if affiliation_lower not in institutions:
					institutions[affiliation_lower] = 1
				else:
					institutions[affiliation_lower] += 1
	
	return _combine_dict_to_list(institutions)
	
	
def frequency_authors(papers):
	print("Getting frequency of authors")
	authors = {}
	
	for paper in papers:
		if not "author" in paper:
			continue
		
		for author in paper['author']:
			if "given" in author and "family" in author:
				author_combined = u"{}{}".format(author[u'given'], author[u'family'])
			elif "given" in author:
				author_combined = author["given"]
			elif "family" in author:
				author_combined = author["family"]
			else:
				author_combined = ""
				
			author_combined = author_combined.encode('utf-8').replace(" ", "")
			if paper['title'][0].encode('utf-8').lower().startswith("book review"):
				author_combined +="_book_review"  # call these out separately so we know who is publishing and who is reviewing
			
			if author_combined not in authors:
				authors[author_combined] = 1
			else:
				authors[author_combined] += 1
	
	return _combine_dict_to_list(authors)

def write_frequencies(items):
	for item in items:
		print("Writing Frequency Info for {}".format(item["name"]))
		with open(item["path"], 'wb') as output_file_handle:
			csv_writer = writer(output_file_handle)
			csv_writer.writerow(["Word", "Frequency"])
			csv_writer.writerows(item["data"])
	
def get_papers(issn=ISSN, offset=0, per_page=PER_PAGE):
	crossref_api = Crossref(mailto=HABANERO_USERNAME)
	return crossref_api.works(filter={"issn": issn}, offset=offset, limit=per_page)  # get a first set of papers

def get_paper_info(issn=ISSN, per_page=PER_PAGE):

	if issn is None or issn == "":
		raise ValueError("ISSN is not defined - can't get paper info - please provide a valid ISSN as argument `issn` to function `get_paper_info`")
		
	num_papers = 0
	collected_info = 0

	paper_info = get_papers(issn, collected_info, per_page)
	num_papers = paper_info['message'][u'total-results']

	print("Found {} papers".format(num_papers))

	papers = []

	while collected_info < num_papers:
		collected_info += per_page
		print("Collecting up to {} papers".format(collected_info))
		
		for paper in paper_info['message']['items']:
			if 'title' in paper:  # if it has a title in the data, we'll keep it, otherwise, skip it
				papers.append(make_data_safe(paper))
		
		sleep(1)
		
		paper_info = get_papers(issn, collected_info, per_page)  # get the next page
	
	return papers

def write_derived_products(papers, base_folder=BASE_FOLDER, issn=ISSN):
	if issn is None or issn == "":
		raise ValueError("ISSN is not defined - can't write out files")
	
	OUTPUT_FILE = os.path.join(base_folder, "{}.csv".format(issn))  # dumps out a CSV with the ISSN as its name in the same directory
	TITLE_FREQUENCY_FILE = os.path.join(base_folder, "{}_title_frequency.csv".format(issn))  # dumps out a CSV with the ISSN as its name in the same directory
	AUTHOR_FREQUENCY_FILE = os.path.join(base_folder, "{}_author_frequency.csv".format(issn))  # dumps out a CSV with the ISSN as its name in the same directory
	INSTITUTION_FREQUENCY_FILE = os.path.join(base_folder, "{}_insitution_frequency.csv".format(issn))  # dumps out a CSV with the ISSN as its name in the same directory

	title_frequency_info = frequency_titles(papers)
	author_frequency_info = frequency_authors(papers)
	institution_frequency_info = frequency_institutions(papers)
	
	print("Writing Paper Info")
	with open(OUTPUT_FILE, 'wb') as output_file_handle:
		csv_writer = DictWriter(output_file_handle, fieldnames=KEYS_TO_KEEP)
		csv_writer.writeheader()
		csv_writer.writerows(papers)
		
	write_frequencies([{"name":"Title", "path":TITLE_FREQUENCY_FILE, "data": title_frequency_info},
						{"name": "Author", "path":AUTHOR_FREQUENCY_FILE, "data": author_frequency_info},
						{"name": "Institution", "path": INSTITUTION_FREQUENCY_FILE, "data": institution_frequency_info}])

if __name__ == "__main__":
	papers = get_paper_info()
	write_derived_products(papers)