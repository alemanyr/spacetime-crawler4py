import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

unique_urls = set() # set of unique urls
project_subdomains = ("ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu")
illegal_paths = ("css","js","bmp","gif","jpe?g","jpeg","ico","png","tiff?","mid","mp2","mp3","mp4", \
				"wav","avi","mov","mpeg","ram","m4v","mkv","ogg","ogv","pdf","ps","eps","tex","ppt", \
				"pptx","doc","docx","xls","xlsx","names","data","dat","exe","bz2","tar","msi","bin", \
				"7z","psd","dmg","iso","epub","dll","cnf","tgz","sha1","thmx","mso","arff","rtf","jar", \
				"csv","rm","smil","wmv","swf","wma","zip","rar","gz")

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
	global unique_urls
	next_links = list()

	with open("content.txt", 'a', encoding="utf-8") as content_file:
		if 200 <= resp.status <= 202:
			# Add url to set of unique URLs
			# Parsing and re-getting the url clears any formatting differences + discards fragment
			parsed_url = urlparse(url)
			unique_urls.add(parsed_url.geturl())

			soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

			a_tags = soup.find_all('a')
			# Extract URLs from <a> tags + append to next_links
			for tag in a_tags:
				tag_url = tag.get('href')
				# Parse + format URL, removing fragment
				formatted_tag_url = urlparse(tag_url).geturl()
				# Don't add a URL we've already visited(ie: present in unique_urls) to next_links
				# Also don't add url to next_links if it's not within the project subdomains
				if not (formatted_tag_url in unique_urls):
					next_links.append(formatted_tag_url)

			# Store all words from webpage
			words = []
			for word in re.finditer(r"[0-9a-zA-Z'-]*[0-9a-zA-Z']+", soup.get_text()):
				word = word.group(0).lower()
				words.append(word)
				# Write to content.txt (data formatted as: <url>|<word list>)
			content_file.write(parsed_url.geturl()+'|'+str(words)+'\n')
	            
	return next_links

def valid_domain(parsed_url):
	netloc = parsed_url.netloc
	# Use the www. stripped netloc to check for domains that are not crawlable
	if netloc.startswith("www."):
		netloc = netloc.strip("www.")
	return any(netloc.endswith(i) for i in project_subdomains) 

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not valid_domain(parsed):
        	return False
        parsed_url_path = parsed.path.lower().split()
        for p in parsed_url_path:
        	if p in illegal_paths:
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
