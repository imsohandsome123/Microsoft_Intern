import json

with open('ptt_dump_20210218_1141.json') as f:
	data = json.load(f)

articles = {}
for i in data['articles']:
	articles[i['article_id']] = i

def search(name): # method = “article_title”, “content”, “messages”
	result = []
	for a_id, a_content in articles.items():
		if name in a_content['article_title']:
			result.append(a_id)
		elif name in i['content']:
			result.append(a_id)
		elif name in i['messages']:
			result.append(a_id)
	return search



search('愛莉莎莎','x')

def output(article_id):
	'''
	given article_id, print the content.
	'''
	







