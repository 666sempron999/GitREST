# -*- coding: utf-8 -*-

from config import Configurator
from datetime import datetime

import requests
import texttable as tt

from timeit import default_timer as timer


def print_table(logins, commits):
    """Функция по данным двум спискам строит консольную таблицу"""

    tab = tt.Texttable()
    x = [[]]
    for i in range(0, 30):
        x.append([i+1, logins[i], commits[i]])

    tab.add_rows(x)
    tab.set_cols_align(['r', 'r', 'r'])

    tab.header(['Место', 'Логин', 'Колличество коммитов'])

    print(tab.draw())



def is_old(created_at, closed_at, days_count):
    """Данная функция проверяет параметр на старость.
    Параметр считается старым, если не закрывается​ в ​течение​ days_count.
    Входные параметры
    created_at
    closed_at
    days_count
    Выходные параметры
    True or False в зависимости от старости параметра

    """
    cr_date = created_at.split("T")[0]
    cl_date = closed_at.split("T")[0]

    cr_date = datetime.strptime(cr_date, "%Y-%m-%d")
    cl_date = datetime.strptime(cl_date, "%Y-%m-%d")

    if (cl_date - cr_date).days > days_count:
        return True
    else:
        return False


def get_popular_contributor(repository):
    """Данная функция возвращает 30 самых активных участников репозитория.
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

    for i in range(0, len(r)):
        authors.append(str(r[i]["author"]["login"]))
        commits.append(int(r[i]["total"]))

    authors.reverse()
    commits.reverse()

    authors = authors[:30]
    commits = commits[:30]

    return authors, commits


def getPullRequestsCount(repository):

    """Данная фкнкция открытых и закрытых pull request.
    Входные параметры:
    repository - репозиторий для поиска
    Выходные параметры:
    open_count - котлличество открытых issues
    close_count - колличество закрытых issues

    """

    open_count = 0
    close_count = 0
    page_number = 1

    url = "https://api.github.com/repos/" + repository + "/pulls?q=&page="\
        + str(page_number) + "&per_page=100&state=all"

    r = requests.get(url).json()

    while len(r) == 100:

        for param in range(0, len(r)):

            if str(r[param]["state"]) == "open":
                open_count += 1

            elif str(r[param]["state"]) == "closed":
                close_count += 1

        page_number += 1

        url = "https://api.github.com/repos/" + repository + "/pulls?q=&page="\
            + str(page_number) + "&per_page=100&state=all"

        r = requests.get(url).json()

    for param in range(0, len(r)):

        if str(r[param]["state"]) == "open":
            open_count += 1

        elif str(r[param]["state"]) == "closed":
            close_count += 1

    return open_count, close_count


def old_pull_request_count(repository):
    """Данная функция позволяет получить колличество старых pull request.
    Pull request старый, если он не закрывается​ в ​течение​ ​30​ ​дней.
    Входные параметры:
    repository - репозиторий для поиска
    Выходные параметры:
    counterOldPull - колличество старых pull request
    """

    counter_old_pull = 0
    page_number = 1

    url = "https://api.github.com/repos/" + repository + "/pulls?q=&page="\
        + str(page_number) + "&per_page=100&state=all"

    r = requests.get(url).json()

    while len(r) == 100:

        for param in range(0, len(r)):

            created = str(r[param]["created_at"])
            closed = str(r[param]["closed_at"])

            if created == "None" or closed == "None":
                continue

            elif is_old(created, closed, 30):
                counter_old_pull += 1

        page_number += 1

        url = "https://api.github.com/repos/" + repository + "/pulls?q=&page="\
            + str(page_number) + "&per_page=100&state=all"

        r = requests.get(url).json()

        for param in range(0, len(r)):

            created = str(r[param]["created_at"])
            closed = str(r[param]["closed_at"])

            if created == "None" or closed == "None":
                continue

            elif is_old(created, closed, 30):
                counter_old_pull += 1

    return counter_old_pull


def getIssueCount(repository):
    """Данная фкнкция открытых и закрытых issues.
    Входные параметры:
    repository - репозиторий для поиска
    Выходные параметры:
    opened - котлличество открытых issues
    closed - колличество закрытых issues
    (opened + closed) - и открытые и закрытые

    """

    url = "https://api.github.com/search/issues?q=repo:" + repository\
        + "+state:open&sort=created&order=asc&page=1&per_page=100"

    r = requests.get(url).json()
    opened = int(r['total_count'])

    url = "https://api.github.com/search/issues?q=repo:" + repository\
        + "+state:closed&sort=created&order=asc&page=1&per_page=100"

    r = requests.get(url).json()
    closed = int(r['total_count'])

    return opened, closed


def getOldIssues(repository):
    """Данная функция врзвращает Количество “старых” issues.
    Issue считается старым, если он не закрывается в течение​​ 14​​ дней.
    Входные параметры:
    repository - репозиторий для поиска
    Выходные параметры:
    old_issues_count - Количество старых issues

    """

    old_issues_count = 0

    opened_issues, closed_issues = getIssueCount(repository)

    pages = ((opened_issues + closed_issues) // 100) + 1  # Получение
    # колличества страниц исходя из колличества открытых и закрытых issues

    for i in range(1, (pages + 1)):
        url = "https://api.github.com/repos/" + repository +\
            "/issues?q=&page=" + str(i) + "&per_page=100&state=all"

        r = requests.get(url).json()

        for param in range(0, len(r)):
            created = str(r[param]["created_at"])
            closed = str(r[param]["closed_at"])

            if created == "None" or closed == "None":
                continue

            elif is_old(created, closed, 14):
                old_issues_count += 1

    return old_issues_count


if __name__ == '__main__':

    start = timer()

    print("Скрипт для анализа репозитория " + Configurator.REPO_NAME)

    print("Самые активные участники")

    logins, commits = get_popular_contributor(Configurator.REPO_NAME)

    print_table(logins, commits)

    print("Количество​​ открытых​​ и​​ закрытых​​ pull​​ requests")

    op, cl = getPullRequestsCount(Configurator.REPO_NAME)
    print("Открырые pull requests -" + str(op))
    print("Закрытые pull requests -" + str(cl))

    print("Количество старых pull requests")

    print("Старые (не закрытые более 30 дней)-" + str(old_pull_request_count(
            Configurator.REPO_NAME)))

    print("Колличество открытых и закрытых issues")

    opened, closed = getIssueCount(Configurator.REPO_NAME)

    print("Открырые issues -" + str(opened))
    print("Закрытые issues -" + str(closed))

    print("Колличество старых issues (не закрытых в течении 14 дней)")

    print("Старые issues -" + str(getOldIssues(Configurator.REPO_NAME)))

    end = timer()
    print("Exec time -", end - start)
