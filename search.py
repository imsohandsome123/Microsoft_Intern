import json

with open('ptt_dump_20210218_1141.json') as f:
  data = json.load(f)

articles = {}

for i in data['articles']:
	# print(i['article_title'])
	print(i['article_id'])
	# print(i['content'])
	# print(i['messages'])
	# exit()
	# exit()
# print(data['M.1613584571.A.0C6'])

# def search(name, method): # method = “article_title”, “content”, “messages”


