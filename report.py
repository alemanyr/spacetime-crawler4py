from urllib.parse import urlparse
from collections import defaultdict

def main():
	word_freq = defaultdict(int)
	longest_page = ('url', 0)
	num_unique_pages = 0
	ics_subdomains = defaultdict(int)
	stop_words = set()
	with open("content.txt", 'r', encoding='utf-8') as content_file, \
		 open("report.txt", 'w', encoding='utf-8') as report:

		for line in content_file:
			num_unique_pages+=1
			
			content = line.rstrip().split('|')
			if content[1] == '*':
				words = []
			else:
				words = content[1].strip('][').replace("'",'').replace('"', '').split(', ')

			if len(words) > longest_page[1]:
				longest_page = (content[0], len(words))

			for word in words:
				if len(word) > 1:
					word_freq[word]+=1

			parsed_url = urlparse(content[0])
			url_netloc = parsed_url.netloc.strip('www.')
			if url_netloc.endswith('ics.uci.edu'):
				ics_subdomains[url_netloc]+=1

		report.write("1. Number of Unique Pages: "+str(num_unique_pages)+'\n')
		report.write("2. Longest Page: "+longest_page[0]+" with "+str(longest_page[1])+" words\n")
		sorted_word_freq = sorted([(word, freq) for word,freq in word_freq.items()], key=lambda x: -x[1])
		report.write("3. 50 Most Common Words\n")
		for i in range(50):
			report.write(sorted_word_freq[i][0]+'\n')

		report.write("4. Number of Subdomains in ics.uci.edu Domain: "+str(len(ics_subdomains))+'\n')
		sorted_ics_subdomains = sorted([(urlparse(sd),np) for sd,np in ics_subdomains.items()], key=lambda x: x[0].netloc)
		for d in sorted_ics_subdomains:
			report.write(d[0].geturl()+', '+str(d[1])+'\n')


if __name__ == "__main__":
	main()
