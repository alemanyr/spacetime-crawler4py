import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
from simhash import Simhash

# The simhash module is from https://github.com/1e0ng/simhash

unique_urls = set() # set of unique urls
project_subdomains = ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")
simhashes = set()
low_content_threshold = 200

def scraper(url, resp):
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
	global unique_urls
	next_links = list()
	with open("content.txt", 'a', encoding="utf-8") as content_file:
		# Add url to set of unique URLs
		# Parsing and re-getting the url clears any formatting differences + discards fragment		
		parsed_url = urlparse(url, allow_fragments=False)
		unique_urls.add(parsed_url.geturl())	
		
		if (200 <= resp.status <= 599) \
			and (resp.raw_response != None) \
			and ('content-type' in resp.raw_response.headers) \
			and ('text/html' in resp.raw_response.headers['content-type']) \
			and (resp.status < 300) \
			and (resp.status != 204):

			soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
			# TODO: Checking for very large files with low information value			
			if bool(soup.find()):
				sh = Simhash(soup.get_text(), reg=r"[a-zA-Z'-]*[a-zA-Z']+")			
				near_dupe_found = False
				# Only scrape webpages that have high content
				if len(sh.tokens) > low_content_threshold:
					for s in simhashes:
						if distance(s, sh.value) < 3:
							near_dupe_found = True
							content_file.write(parsed_url.geturl()+'|'+'*\n')
							break
					if not near_dupe_found:
						a_tags = soup.find_all('a', href=True)
							# Extract URLs from <a> tags + append to next_links
						for tag in a_tags:
							tag_url = tag.get('href')
							formatted_tag_url = urlparse(tag_url)
							# Check if href is a relative or absolute path
							if formatted_tag_url.scheme == '' and formatted_tag_url.netloc == '':
								final_url = urljoin(parsed_url.geturl(), formatted_tag_url.geturl(), allow_fragments=False)
							else:
								final_url = urlparse(formatted_tag_url.geturl(), allow_fragments=False).geturl()
							# Don't add a URL we've already visited(ie: present in unique_urls) to next_links
							if not (final_url in unique_urls):
								next_links.append(final_url)
						# Write to content.txt (data formatted as: <url>|<word list>)
						content_file.write(parsed_url.geturl()+'|'+str(sh.tokens)+'\n')
						simhashes.add(sh.value)	
				else:
					content_file.write(parsed_url.geturl()+'|'+'*\n')
			else:
				content_file.write(parsed_url.geturl()+'|'+'*\n')
		else:
			# Check if current url is redirect
			if resp.status == 302:
				formatted_redirect_url = urlparse(resp.raw_response.url, allow_fragments=False).geturl()
				if not (formatted_redirect_url in unique_urls):
					next_links.append(formatted_redirect_url)
			content_file.write(parsed_url.geturl()+'|'+'*\n')
				
	return next_links

# Helper function for simhash from https://github.com/1e0ng/simhash

def distance(v1, v2):
        x = (v1 ^ v2) & ((1 << 64) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans


def valid_domain(parsed_url):
	netloc = parsed_url.netloc
	# Use the www. stripped netloc to check for domains that are not crawlable
	if netloc.startswith("www."):
		netloc = netloc.strip("www.")

	valid = False
	# Check for domain: today.uci.edu/department/information_computer_sciences/ and allow it
	if (netloc.endswith("today.uci.edu")) and ("/department/information_computer_sciences/" in parsed_url.path):
		valid = True

	# Check if domain in allowed project domains
	elif any(netloc.endswith(i) for i in project_subdomains):
		valid = True

	# Filter out urls with queries
	if (parsed_url.query != ""):
		valid = False
	return valid

def is_valid(url):
	try:
		parsed = urlparse(url)
		parsed_path = parsed.path.lower()
		parsed_query = parsed.query.lower()
		if parsed.fragment != '':
			return False
		if parsed.scheme not in set(["http", "https"]):
			return False
		if not valid_domain(parsed):
			return False
		return not (re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz"
			+ r"|ppsx|r|java|in|py|scm|rkt|txt"
			+ r"|svg|ss|odc|sas|war|rmd|ds|img|apk|cp|z|lsp|pov|mpg)$", parsed_path) \
			or re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz"
			+ r"|ppsx|r|java|in|py|scm|rkt|txt"
			+ r"|svg|ss|odc|sas|war|rmd|ds|img|apk|cp|z|lsp|pov|mpg)$", parsed_query))

	except TypeError:
		print ("TypeError for ", parsed)
		raise
