# -*- coding: utf-8 -*-

from config import Configurator
from datetime import datetime
import json
import requests
import texttable as tt

def getPagesCount(repository,parametr):
	"""
	Данная функция возвращает общее колличество страниц параметра для указаного репозитория
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	countElement - колличество страниц
	"""
	
	countElement = 0
	url = "https://api.github.com/repos/"+ repository +"/" + parametr +"?q=&page=1&per_page=100&state=all"
	r = requests.get(url).json()
	
	while len(r) == 100:
		countElement += 1
		url = "https://api.github.com/repos/"+ repository +"/pulls?q=&page="+ str(countElement) +"&per_page=100&state=all"
		r = requests.get(url).json()

	return countElement

def isOld(created_at,closed_at,daysCount):
	"""
	Данная функция проверяет параметр на старость.
	Параметр считается старым, если он не закрывается​ в ​течение​ daysCount дней.
	Входные параметры
	created_at
	closed_at
	daysCount
	Выходные параметры
	True or False в зависимости от старости параметра
	"""
	cr_date = created_at.split("T")[0]
	cl_date = closed_at.split("T")[0]

	cr_date = datetime.strptime(cr_date, "%Y-%m-%d")
	cl_date = datetime.strptime(cl_date, "%Y-%m-%d")

	if (cl_date - cr_date).days > daysCount:
		return True
	else:
		return False

def printTable(logins,commits):
	"""
	"""
	tab = tt.Texttable()
	x = [[]]
	for i in range(0,30):
		x.append([i+1,logins[i],commits[i]])

	tab.add_rows(x)
	tab.set_cols_align(['r','r','r'])

	tab.header(['Место', 'Логин', 'Колличество коммитов'])

	print(tab.draw())

def getPopularContributor(repository):
	"""
	Данная функция возвращает 30 самых активных участников репозитория. 
	Активность определяется по колличеству коммитов.
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	authors - список авторов коммитов 
	commits - колличество коммитов каждого автора
	"""
	authors = []
	commits = []

	url = "https://api.github.com/repos/" + repository + "/stats/contributors"
	r = requests.get(url).json()

	for i in range(0,100):
		authors.append(str(r[i]["author"]["login"]))
		commits.append(int(r[i]["total"]))

	authors.reverse()
	commits.reverse()

	authors = authors[:30]
	commits = commits[:30]

	return authors,commits

def getPullRequestsCount(repository):
	"""
	Данная фкнкция открытых и закрытых pull request.
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	openCount - котлличество открытых issues
	closeCount - колличество закрытых issues
	"""
	
	openCount = 0
	closeCount = 0

	pages = getPagesCount(repository,"pulls")

	for i in range(1,(pages + 1)):
		url = "https://api.github.com/repos/"+ repository +"/pulls?q=&page=" + str(i) + "&per_page=100&state=all"
		r = requests.get(url).json()

		for param in range(0,len(r)):
			if str(r[param]["state"]) == "open":
				openCount += 1
			elif str(r[param]["state"]) == "closed":
				closeCount += 1

	return openCount,closeCount



def OldPullRequestCount(repository):
	"""
	Данная функция позволяет получить колличество старых pull request.
	Pull request считается старым, если он не закрывается​ ​ в ​ ​ течение​ ​ 30​ ​ дней.
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	counterOldPull - колличество старых pull request
	"""

	counterOldPull = 0

	pages = getPagesCount(repository,"pulls")

	for i in range(1,(pages + 1)):
		url = "https://api.github.com/repos/"+ repository +"/pulls?q=&page=" + str(i) + "&per_page=100&state=all"
		r = requests.get(url).json()

		for param in range(0,len(r)):

			created = str(r[param]["created_at"])
			closed = str(r[param]["closed_at"])

			if created == "None" or closed == "None":
				continue
			elif isOld(created,closed,30) == True:
				counterOldPull += 1

	return counterOldPull


def getOldIssues(repository):
	"""
	Данная функция врзвращает Количество “старых” issues.
	Issue считается старым, если он не закрывается в течение​​ 14​​ дней.
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	oldIssuesCount - Количество старых issues
	"""

	oldIssuesCount = 0

	pages = getPagesCount(repository,"issues")
	
	for i in range(1,(pages + 1)):
		url = "https://api.github.com/repos/"+ repository +"/issues?q=&page=" + str(i) + "&per_page=100&state=all"
		r = requests.get(url).json()

		for param in range(0,len(r)):
			created = str(r[param]["created_at"])
			closed = str(r[param]["closed_at"])

			if created == "None" or closed == "None":
				continue
			elif isOld(created,closed,14) == True:
				oldIssuesCount += 1

	return oldIssuesCount

def getIssueCount(repository):
	"""
	Данная фкнкция открытых и закрытых issues.
	Входные параметры:
	repository - репозиторий для поиска
	Выходные параметры:
	opened - котлличество открытых issues
	closed - колличество закрытых issues
	(opened + closed) - и открытые и закрытые

	"""
	url = "https://api.github.com/search/issues?q=repo:" + repository + "+state:open&sort=created&order=asc&page=1&per_page=100"
	r = requests.get(url).json()
	opened = int(r['total_count'])

	url = "https://api.github.com/search/issues?q=repo:" + repository + "+state:closed&sort=created&order=asc&page=1&per_page=100"
	r = requests.get(url).json()
	closed = int(r['total_count'])

	return opened,closed

#=====================================================================================
if __name__ == '__main__':
    print("Скрипт для анализа репозитория", Configurator.REPO_NAME)

    print("1)Самые активные участники")

    logins,commits = getPopularContributor(Configurator.REPO_NAME)
    printTable(logins,commits)

    print("2)Количество​​ открытых​​ и​​ закрытых​​ pull​​ requests")

    op, cl = getPullRequestsCount(Configurator.REPO_NAME)
    print("Открырые pull requests -",op)
    print("Закрытые pull requests -",cl)

    print("3)Количество старых pull requests")
    print("Старые (не закрытые более 30 дней)-",OldPullRequestCount(Configurator.REPO_NAME))

    print("4)Колличество открытых и закрытых issues")

    opened, closed = getIssueCount(Configurator.REPO_NAME)
    print("Открырые issues -",opened)
    print("Закрытые issues -",closed)

    print("5)Колличество старых issues (не закрытых в течении 14 дней)")
    print("Старые issues -",getOldIssues(Configurator.REPO_NAME))


"""
При привышении колличества неавторизованых запросов получается следующее сообщение:

"API rate limit exceeded for X.X.X.X. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)"
"""
