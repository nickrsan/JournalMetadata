import get_papers
import fire

def run(issn, email_address):
	"""
		:param issn: string ISSN of the journal to download
		:param email_address: Provide your email address as your username for the CrossRef API (does *not* need to be
			preregistered). Will not be stored by this script. CrossRef uses it to get in touch with you if you or 
			this script misuse the service so the issue can be resolve - if you provide an invalid email address,
			they may ban you instead of getting in touch - so be nice and provide your actual email!
	"""
	papers = get_papers.get_paper_info(issn=issn, username=email_address)
	get_papers.write_derived_products(papers=papers, issn=issn)

if __name__ == '__main__':
  fire.Fire(run)