from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from wtforms import Form, StringField, SubmitField

app = Flask(__name__)


class SearchForm(Form):
    user = StringField('Github Username')
    submit = SubmitField('Search')

@app.route('/', methods=['GET', 'POST'])
def search_for_repositories():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return get_repositories(form)
    return render_template('index.html', form=form)


@app.route('/search_result')
def get_repositories(search):

    username = search.user.data
    url = 'https://github.com/' + username
    html = requests.get(url).text
    response = requests.get(url)
    response_code = response.status_code
    if response_code != 200:
        print("Error ocurred")
        return
    html_content = response.content
    all_repositories = []
    dom = BeautifulSoup(html_content, 'html.parser')

    repo_attributes = dom.select("a.no-wrap, span.mr-3")
    stars_list = []
    for star in repo_attributes:
        if ("octicon octicon-star" in str(star)):
            star = str(star).splitlines()
            if star[2] == "</span>":
                star[2] = '0'
            star[2] = star[2].replace(',', '')
            stars_list.append(star[2].strip())

    repositories = dom.select("div.flex-auto h3")
    j = 0
    for repo in repositories:
        href_link = repo.a.attrs["href"]
        url_link = "https://github.com{}".format(href_link)
        username_replace = "/"+username+"/"
        name = href_link.replace(username_replace, '', 1)
        repo_list = [name, stars_list[j], url_link]
        all_repositories.append(repo_list)
        j += 1

    all_repositories.sort(key=lambda x: int(x[1]), reverse=True)

    return render_template('result.html', get_repositories = all_repositories)


if __name__ == '__main__':

    app.run()
