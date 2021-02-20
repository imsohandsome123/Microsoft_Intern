import json

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

with open('ptt_dump_20210218_1141.json') as f:
	data = json.load(f)

articles = {}

for i in data['articles']:
	articles[i['article_id']] = i
	# print(i['article_id'])
	# print(i['content'])
	# print(i['messages'])
	# exit()
	# exit()

search('愛莉莎莎','x')

# for i in articles:
# 	print(i)
# 	exit()
# print(data['M.1613584571.A.0C6'])





