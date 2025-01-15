# Python program to convert wiki-format data to CSV
#  Data from https://en.wikipedia.org/wiki/Potential_re-accession_of_the_United_Kingdom_to_the_European_Union
# Robert MacDonald January 2025

# Data example:
# new row        >> |-
# start/end date >> |{{opdrts|2|3|Jan|2024|year}}
# Pollster       >> ||[https://yougov.co.uk/politics/articles/48260-four-years-after-brexit-what-future-forms-of-relationship-with-the-eu-would-britons-support YouGov]
# Client         >> |''N/A''
# Sample Size    >> |2,016
# Rejoin         >> |style="background:#DDE0EE"|'''51%'''
# Stay out       >> |36%
# Neither        >> |13%
# Lead           >> |style="background:#4477AA;color:#FFFFFF;"|15%

# Created CSV has columns:
# start_date,end_date,pollster_link,pollster_name,client,samplesize,rejoin,stay_out,neither

# Read data from these files
datafiles = ["2020.txt", "2021.txt", "2022.txt", "2023.txt", "2024.txt", "2025.txt"]

# Imports
import datetime
import pandas as pd

# Function to interpret opdrts notation
# Example input: {{opdrts|29|3|Jan|2024|year}}
# Returns tuple of startDate and endDate
# https://en.wikipedia.org/wiki/Template:Opdrts
def parseOpdrts(s):
    s = s.strip() # remove whitespace either side
    if s[0:9] != "{{opdrts|" or s[-2:] != "}}":
        raise Exception("opdrts template must be in format {{opdrts|29|3|Jan|2024|year}}. {{opdrts| and }} not found.")
    parts = s[9:-2].split("|")

    if len(parts) < 3:
        raise Exception("opdrts template must be in format {{opdrts|29|3|Jan|2024|year}}. Minimum of three parts between | symbols is required.")

    if parts[0] != '':
        startDay = int(parts[0])
    else:
        startDay = int(parts[1]) #start day is optional so it is equal to end day if not given
    endDay = int(parts[1])

    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    try:
        endMonth = int(parts[2])
    except ValueError:
        if parts[2].lower() in months.keys():
            endMonth = months[parts[2].lower()]
        else:
            raise Exception(f"{parts[2]} in opdrts is not a valid month.  Month should be Jan, Feb, etc.")
        
    if int(parts[3]) > 1900 and int(parts[3]) < 9999:
        endYear = int(parts[3])
    
    if endDay >= startDay:
        startMonth = endMonth
        startYear = endYear
    else:
        if endMonth == 1:
            startMonth = 12
            startYear = endYear - 1
        else:
            startMonth = endMonth - 1
            startYear = endYear

    startDate = datetime.date(startYear, startMonth, startDay)
    endDate = datetime.date(endYear, endMonth, endDay)

    return (startDate, endDate)

# Function to parse a percentage like 23% into an int
def parsePercent(p):
    p = p.strip()
    if p[-1:] != "%":
        raise Exception(f"Percentage in {p} cannot be parsed. Must end with %.")
    p = p.replace("%", "")
    try:
        return float(p)/100
    except ValueError:
        raise Exception(f"Percentage number in {p} cannot be parsed. Cannot parse to int with python int().")

# Function to parse a wiki external link
# [https://url/ Text]
# Returns tuple of ("https://url/", "Text")
def parseExtLink(l):
    l = l.strip()
    if l[0] != "[" or l[-1] != "]":
        raise Exception(f"Link {l} cannot be parsed, cannot find start or end [ and ]")
    if l[0:2] == "[[" or l[-2:] == "]]":
        raise Exception(f"Link {l} appears to be an internal link with [[ and ]], not external with [ and ].")
    parts = l[1:-1].split(" ", 1)
    return (parts[0], parts[1])

## Function to parse a pollster
def parsePollster(p):
    p = p.strip()
    if p[0] == "[" and p[-1] == "]":
        return parseExtLink(p)
    else:
        return ("", p)

# Function to parse rows of the wikitable
# Returns a dictionary
def parseRow(r):
    try:
        # Remove styles and other things
        newR = []
        for x in r:
            x = x.strip() # remove leading and trailing whitespace
            x = x.replace("'''", "") # remove bold '''
            x = x.replace("''", "") # remove italics ''
            if x[0:6] == "style=":
                ps = x.split("|", 1)
                x = ps[1]
            if x[0:1] == "|":
                x = x[1:]
            newR.append(x)
        r = newR
        
        (startDate, endDate) = parseOpdrts(r[0])
        (pollsterLink, pollsterName) = parsePollster(r[1])
        client = r[2]
        sampleSize = int(r[3].replace(",", ""))
        rejoin = parsePercent(r[4])
        stayOut = parsePercent(r[5])
        neither = parsePercent(r[6])

        return {"start_date": startDate,
                "end_date": endDate,
                "pollster_link": pollsterLink,
                "pollster_name": pollsterName,
                "client": client,
                "sample_size": sampleSize,
                "rejoin": rejoin,
                "stay_out": stayOut,
                "neither": neither }
    except Exception as e:
        print(f"Exception raised whilst parsing row: {r}")
        raise e

# Function to read a wikitable from a file handle
# Returns a list of lists
# [[row1colA, row1xolB, ...], [row2colA, row2colB, ...], ...]
def parseTable(f):
    rows = []
    thisRow = []
    for line in f:
        if line.strip() == "|-":
            # New Row
            if len(thisRow) > 0:
                rows.append(thisRow)
                thisRow = []
        else:
            thisRow.append(line.strip()[1:])
    if len(thisRow) > 0:
        rows.append(thisRow)
    return rows

# Parse files
allData = []
for datafile in datafiles:
    f = open(datafile, 'r')
    for row in parseTable(f):
        allData.append(parseRow(row))

# Write CSV file with pandas
df = pd.DataFrame(allData)
df = df.sort_values(by='end_date')
df.to_csv("output.csv")