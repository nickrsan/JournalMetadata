# Get Journal Metadata

Dumps a CSV of information about a single journal as a spreadsheet, as well as three separate CSVs with frequency analysis/counts of authors, words in titles, and
institutions publishing (with some imperfect filtering to clean each of those up).

All data comes from the [CrossRef](https://www.crossref.org/) API, which helpfully catalogs this information, then provides a programmatic interface to it.

## Requirements

Requires the package `habanero` - an interface to the CrossRef API in Python. Available on PyPI (via Pip) and GitHub. Can be installed with `python -m pip install habanero`

This code was written and tested in Python 2, but should be Python 3 compatible

## Usage

Currently, edit the script - the first two constants near the top `HABANERO_USERNAME` and `ISSN` must be filled in with your email address, and the ISSN of the
journal whose data you want to download, respectively. Save and run the script, and it will output files in the same directory as the script (Not the CWD). Your email
address does not need to be registered with CrossRef, but you *should* provide one so that if the script misbehaves they can get in touch with you instead of banning
you.

Output location can be modified by changing BASE_FOLDER.

For automation of many journals using this script, you can import it and use its functions. For example:

```python
	import get_papers
	
	get_papers.HABANERO_USERNAME = "me@myemailaddress.com"  # make this real though - they use it to contact you before cutting you off if your script misbehaves
	paper_data = get_papers.get_paper_info(issn="1111-1111")  # provide the ISSN for the journals you'd like to work with
	get_papers.write_derived_products(paper_data)  # writes the outputs

```

You can put that last two lines there in a loop to cover many ISSNs, etc, or write a script that accepts command line arguments. Those are the two core functions -
everything else just supports each of those.

## License
MIT License

## Interpretation and Limitations
As written, only articles with titles are kept. Outputs in the main spreadsheet will still have some JSON formatting in them - it's for your interpretation or future parsing, but this script doesn't parse everything down to the individual item level (eg: it won't split out multiple authors in the main spreadsheet - it keeps
one author field)

Frequency analysis is done on titles by splitting and counting the occurrence (non-case sensitive) of every word longer than two letters. You'll see some artifacts, ignore those and just look for items that might be of use in determining themes. I highly recommend bringing the datasets into Excel and turning the top row into filters so you can sort on the frequency field.

For authors, first and last names were combined (where both existed) and the number of papers for each author were counted. Papers with multiple authors were attributed to all authors. My journal has a lot of book reviews, so it splits out paper titles that start with "book review" separately and provides counts for authors both for journal articles and for book reviews.

For institutions, parsing the information is tricky. I just wanted to see which universities (or other research institutions), but not departments, centers, etc, were publishing in the journal the most. But most author affiliations include a lot of other information, and it's not formatted universally in the same way. So, what this script does is, before counting an affiliation, it splits the affiliation into pieces using commas as a delimiter. It then looks for a piece that has the word "university" in it and uses that as the affiliation if it exists. If it doesn't exist at all, then the entire affiliation is used for counting. As a result, all affiliations will most likely be undercounts, but they will have at least that many publications in the journal, because it's possible that other papers appeared that didn't match this rule - you'll still see them in the frequency analysis, just as standalone items.

The main takeaway here is that all this information should be used to discover trends rather than to report on specifics and relative ratios. In my paper, I probably won't talk about the exact number of papers published by a specific university, but instead how clearly Progress in Physical Geography is dominated by UK universities, etc.

A good use for a lot of this information might be to look for keywords used in lots of titles, then go find the more highly cited article (citation info is available in the main spreadsheet as column is-referenced-by-count) and then actually read/skim that article. Etc. Just a thought.

The last thing I'll mention is that not all journals have all of the same information. At least one journal I pulled for a classmate didn't have institutional affiliations attached, so the script couldn't analyze that part. Sorry!