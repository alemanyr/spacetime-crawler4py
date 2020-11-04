from urllib.parse import urlparse
from collections import defaultdict

stopwords = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", \
"you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', \
'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', \
'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', \
'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', \
'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', \
'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', \
'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', \
'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', \
'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', \
'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', \
"should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", \
'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", \
'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', \
"shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}

def main():
	word_freq = defaultdict(int)
	longest_page = ('url', 0)
	num_unique_pages = 0
	ics_subdomains = defaultdict(int)
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
				if (not (word in stopwords)) and (len(word) > 1):
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
