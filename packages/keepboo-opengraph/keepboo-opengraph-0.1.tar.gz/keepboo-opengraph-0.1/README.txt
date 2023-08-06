# opengraph

OpenGraph parser used on KEEPBOO

This project is used to fetch Open Graph data from given url or html.

### Installation

    pip install keepboo-opengraph

### Usage

    from keepboo.opengraph import OpenGraph

    og = OpenGraph(url="http://keepboo.com/")
    print 'json', og.to_json()
    print 'html', og.to_html()