from urllib.parse import urlparse
from collections import defaultdict

def main():
	word_freq = defaultdict(0)
	longest_page = ('url', 0)
	num_unique_pages = 0
	ics_subdomains = defaultdict(0)
	stop_words = set()
	with open("content.txt", 'r', encoding='utf-8') as content_file, \
		 open("stop_words.txt", 'r', encoding='utf-8') as stop_words_file, \
		 open("report.txt", 'w', encoding='utf-8') as report:

		for w in stop_words_file:
			stop_words.add(w.rstrip())
		for line in content_file:
			num_unique_pages+=1
			content = line.split('|')
			words = content[2].strip('][').split(', ')

			if len(words) > longest_page[1]:
				longest_page = (content[0], content[2])

			for word in words:
				if word not in stop_words:
					word_freq[word]+=1

			parsed_url = urlparse(content[0])
			url_netloc = parsed_url.netloc.split('.')
			if len(url_netloc) >= 4 and '.'.join(url_netloc[-3:-1]) == 'ics.uci.edu':
				full_subdomain=parsed_url.geturl()
				if full_subdomain in ics_subdomains:
					ics_subdomains[full_subdomain]+=1
				else:
					ics_subdomains[full_subdomain]=1

	
	report.write("1. Number of Unique Pages: "+str(num_unique_pages)+'\n')
	report.write("2. Longest Page: "+longest_page[0]+" with "+str(longest_page[1])+" pages\n")
	sorted_word_freq = sorted([(word, freq) for word,freq in word_freq.items()], key=lambda x: -x[1])
	report.write("3. 50 Most Common Words\n")
	for i in range(50):
		report.write(sorted_word_freq[i][0]+'\n')

	#This is not properly formatted yet
	report.write("4. Number of Subdomains in ics.uci.edu Domain: "+str(len(ics_subdomains)))
	sorted_ics_subdomains = sorted([(urlparse(sd),np) for sd,np in ics_subdomains.items()], key=lambda x: x[0].netloc)
	for d in sorted_ics_subdomains:
		report.write(d[0].geturl()+', '+str(d[1]))


if __name__ is "__main__":
	main()
