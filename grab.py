import requests
from lxml import html


def parse_stats(elem):
    statdict = {}
    for e in elem:
        try:
            prev = False
            for chone in e.getchildren():
                if prev:
                    prev = False
                    continue
                for chtwo in e.getchildren():
                    if (chone.get('class') == chtwo.get('class')) and (chone.text_content() != chtwo.text_content()):
                        statdict[chone.text_content().strip(':')] = chtwo.text_content()
                        prev = True
        except Exception as e:
            print('{}'.format(e))
    return statdict


def fetch(url):
    results = []
    page = requests.get(url)
    page_tree = html.fromstring(page.content)
    elements = page_tree.xpath('//*[@class="work blurb group"]')

    site_url = "http://archiveofourown.org"

    for element in elements:
        link = element.xpath("div/h4/a[1]")[0]
        summary = element.xpath("blockquote/p/text()")
        tags = element.xpath('ul/li/a[1][not(class="warnings")]')
        fandoms = element.xpath("div/h5/a")
        iscomplete = element.xpath("div/ul/li[4]/a/span")[0]
        stats = element.xpath('dl')

        href = link.get("href")
        status = iscomplete.get("title")
        title = link.text_content()
        taglist = ([tag.text_content() for tag in tags])
        fandlist = ([f.text_content() for f in fandoms])

        if summary:
            summary = "\n".join([str(x) for x in summary])
        else:
            summary = "No summary."

        results.append({
            "title": title,
            "link": site_url + href,
            "fandoms": ", ".join([str(x) for x in fandlist]),
            "summary": summary,
            "tags": ", ".join([str(x) for x in taglist]),
            "status": status,
            "stats": parse_stats(stats)
        })

    return results


if __name__ == '__main__':
    fetch("http://archiveofourown.org/tags/Angel's%20Feather/works")
