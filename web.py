import requests
from bs4 import BeautifulSoup


def search_web(query):
    response = requests.get(query.replace("|", ""))
    soup = BeautifulSoup(response.text,
                             "html.parser")

    results = {"links": [],
               "link_text": [],
               "text": [],
               "span_text": []}

    link_objects = soup.find_all("a")
    for a in link_objects:
        results["link_text"].append(a.text)
        if a.has_attr('href'):
            results["links"].append(a["href"])

    paragraph_objects = soup.find_all("p")
    for p in paragraph_objects:
        results["text"].append(p.text)

    # span_objects = soup.find_all("span")
    # for span in span_objects:
        # results["span_text"].append(span.text)

    return str(results)

# r = search_web("https://www.google.com/search?q=grey+cats")
# print(r)