# Overview
This repository contains code to generate the graph on the Wikipedia page [Potential re-accession of the United Kingdom to the European Union](https://en.wikipedia.org/wiki/Potential_re-accession_of_the_United_Kingdom_to_the_European_Union)

![Graph of opinion poll results on the subject of whether the United Kingdom should rejoin the European Union, with LOESS curves](https://upload.wikimedia.org/wikipedia/commons/e/e8/Opinion_polling_on_the_whether_the_United_Kingdom_should_rejoin_the_European_Union.svg)

# Acknowledments
The graph has been created and regularly updated since 2022 by [User:Ralbegen](https://en.wikipedia.org/wiki/User:Ralbegen) and [their code](https://en.wikipedia.org/wiki/User:Ralbegen/Opinion_poll_code) slightly influenced aspects of what is in this repository. The new graph is itended to be identical to their graph.

At the time of writing, [User:Ralbegen](https://en.wikipedia.org/wiki/User:Ralbegen) has not updated the graph for 6 months and has not edited Wikipedia at all for 4 months.  Other users have requested updates without response, so I created this project. Input from [User:Ralbegen](https://en.wikipedia.org/wiki/User:Ralbegen) is welcomed. 

# .txt files
The files like 2024.txt etc are copies of the wiki table markup from the [page source](https://en.wikipedia.org/w/index.php?title=Potential_re-accession_of_the_United_Kingdom_to_the_European_Union&action=edit&section=6).

To update them, copy and paste directly from the wiki source. 

The files must start with a line `|-` so don't copy and paste the headings of the tables.

Example entry:
```Wikitext
|-
|{{opdrts|6|8|Dec|2024|year}}
|[https://d3nkl3psvxxpe9.cloudfront.net/documents/Topline_Eurotrack_Dec24.pdf YouGov]
|''Eurotrack''
|2,119
|style="background:#DDE0EE"|'''45%'''
|32%
|23%
|style="background:#4477AA;color:#FFFFFF;"|13%
```

# dataconvert.py
`dataconvert.py` reads all the .txt files, parses them, and generates `output.csv`.

If a new year/file exists, add it to `datafiles` around line 20:
```python
# Read data from these files
datafiles = ["2020.txt", "2021.txt", "2022.txt", "2023.txt", "2024.txt"]
```

Example of the top of `output.csv` is:
```csv
,start_date,end_date,pollster_link,pollster_name,client,sample_size,rejoin,stay_out,neither
12,2020-02-04,2020-02-05,https://docs.cdn.yougov.com/v17h1b66px/Handelsblatt_ToplineResults_Feb2020_public.pdf,YouGov,Handelsblatt,1578,0.42,0.4,0.2
11,2020-02-04,2020-02-07,https://www.bmgresearch.co.uk/bmg-independent-labour-policies-popular-but-many-want-change-in-direction-2/,BMG Research,The Independent,1503,0.42,0.46,0.12
10,2020-03-03,2020-03-06,https://www.bmgresearch.co.uk/bmg-polling-results-on-behalf-of-the-independent/,BMG Research,The Independent,1337,0.4,0.48,0.12
9,2020-03-24,2020-03-26,https://www.ncpolitics.uk/wp-content/uploads/sites/5/2020/04/bloomberg-brexit-2020-03.pdf,Number Cruncher Politics,Bloomberg,1010,0.38,0.47,0.14
8,2020-04-07,2020-04-09,https://www.bmgresearch.co.uk/bmg-polling-results-on-behalf-of-the-independent-2/,BMG Research,The Independent,1371,0.43,0.47,0.1
...
```

# eugraph.r
The R file `eugraph.r` generates the actual graph in `Opinion_polling_on_the_whether_the_United_Kingdom_should_rejoin_the_European_Union.svg`

Around line 54 onwards, there are some interesting values to change if re-generating the graph.

```r
scale_y_continuous(labels = percent_format(accuracy = 1),
                   breaks = seq(from = 0, to = .6, .1),   # Set breaks on Y axis - update if changing limits in line below
                   limits = c(-.01, 0.6 + .01),           # Set max 60% on graph
                   expand = c(0, 0)) +
scale_x_date(date_labels = "%b %Y",
             breaks = seq(from = ymd("2020-01-01"), to = ymd("2025-07-01"), by = "6 months"),    # Y axis breaks - update if changing limits below
             date_minor_breaks = "1 month",
             limits = c(ymd("2019-12-01"), ymd("2025-08-01")),  # Sets the date range on the X axis
                                                                # Change second date to around 6 months in future when re-running
             expand = c(0, 0)) +
```

# Possible further improvements
* I don't really know R and the code or output can probably be improved
* The SVG generated is not scalable, this can possibly be fixed in R
* Fully automate download of poll data from the wikipedia page

Pull requests welcome :)
