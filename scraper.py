import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

# Global vars for storing report question info
unique_urls = set() # set of unique urls
longest_page = ('name', 0) # tuple of page name and word count
word_freq = dict() # word: freq
ics_subdomains = dict() # subdomain: pages per subdomain

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
	global unique_urls, longest_page, word_freq, ics_subdomains
	next_links = list()

	with open(url) as html_file:
		# Add url to set of unique URLs
		# Parsing and re-getting the url clears any formatting differences + discards fragment
		parsed_url = urlparse.urlsplit(url)
		unique_urls.add(parsed_url.geturl())

		# Update ics_subdomains dict if necessary
		# This will split the path as such: http://vision.ics.uci.edu/projects.html -> ['vision','ics','uci','edu']
		split_url_path = parsed_url.path.split('/')[0].split('.')
		# If the page is an ics.uci.edu subdomain
		if len(split_url_path) >= 4 and '.'.join(split_url_path[-3:-1]) == 'ics.uci.edu':
			# Update the ics_subdomains dict
			full_subdomain = '.'.join(split_url_path)
			if full_subdomain in ics_subdomains:
				ics_subdomains[full_subdomain] += 1
			else:
				ics_subdomains[full_subdomain] = 1

		soup = BeautifulSoup(html_file, 'lxml')

		# Extract all <a> tags (hyperlink tags)
		a_tags = soup.find_all('a')
		# Extract URLs from <a> tags + append to next_links
		for tag in a_tags:
			tag_url = tag.get('href')
			# Parse + format URL, removing fragment
			formatted_tag_url = urlparse.urlsplit(tag_url).geturl()
			# Don't add a URL we've already visited(ie: present in unique_urls) to next_links
			# TODO Also don't add url to next_links if it's not within the project subdomains
			if not (formatted_tag_url in unique_urls):
				next_links.append(formatted_tag_url)

		# TODO create list of all words on page(not just unique words, all words)
		# should eliminate capitalization, etc.
		word_list = list()

		# Update longest page variable if necessary
		if len(word_list) > longest_page[1]:
			longest_page = (parsed_url, len(word_list))

		# Update word frequency dictionary
		# TODO filter stop words here? Or later?
		for word in word_list:
			if word in word_freq:
				word_freq[word] += 1
			else:
				word_freq[word] = 1

	return next_links

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
