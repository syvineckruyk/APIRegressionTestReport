#!/usr/bin/python
__author__ = 'steven'

import sys
import os
import traceback
from ast import literal_eval


def main(path):
    try:
        files = listdir_fullpath(path)
        print files
        keys = get_common_keys(files)
        results, headers = check_keys(keys, files)
        print headers, results
        results_to_text(results, "results.txt", headers)
        results_to_vega()
        for file in files:
            file_name_to_columns(file)
    except:
        error = sys.exc_info()[0]
        print "error", error
        print traceback.format_exc()

def file_name_to_columns(filename):
    attribs = ["port", "user", "endpoint", "criteria"]
    filename = os.path.split(filename)[1]
    columns = filename.split('_')
    fileattribs = {}
    for attrib in attribs:
        fileattribs[attrib] =  columns[attribs.index(attrib)]
    return fileattribs

def results_to_text(results, outputfile, headers=None):
    print headers
    report = open(outputfile, "w+")
    if headers is not None:
        reportheaders = "\t {headers}\n".format(headers="\t".join(headers))
        report.writelines(reportheaders)
    reportdata = "\n".join(["\t".join(map(str, [str(value.values())[1:-1] for value in result])) for result in results])
    report.write(reportdata)
    report.close()


def read_file(inputfile):
    try:
        data = literal_eval(open(inputfile, 'r').read())
        #print "{no_records} records were read from file {inputfile}".format(no_records=len(data), inputfile=inputfile)
        return data
    except Exception as error:
        error = sys.exc_info()[0]
        print "file {inputfile} could not be read : {exception}".format(inputfile=inputfile, error=error.message)


def get_values(key, recordlist):
    values = []
    for record in recordlist:
        values.append(record[key])
    return values


def sum_values(key, valuelist):
    aggr = sum(valuelist)
    return aggr


def get_common_keys(filelist):
    setlist = []
    for file in filelist:
        filesetlist = []
        data = read_file(file)
        for record in data:
            keys = set(record)
            filesetlist.append(keys)
        filekeys = set.intersection(*filesetlist)
        setlist.append(filekeys)
    keys = list(set.intersection(*setlist))
    return keys


def check_keys(keys, filelist):
    tests = []
    for file in filelist:
        test = [{"file": file}]
        data = read_file(file)
        badkeys = []
        for key in keys:
            try:
                result = {key: sum_values(key=key, valuelist=get_values(key=key, recordlist=data))}
                test.append(result)
            except Exception as error:
                print error
                print file, key
                badkeys.append(key)
                #keys.remove(key)
                pass
        tests.append(test)
        if len(badkeys) > 0:
            for key in badkeys:
                keys.remove(key)
    return tests, keys


def get_apps(inputfile):
    data = read_file(inputfile)
    apps = get_values(key="app", recordlist=data)
    where = create_where_clause(key="app_name", list=apps)
    return apps, where


def create_where_clause(key, elementlist, base="WHERE"):
    elements = ["{key} = \"{element}\"".format(key=key, element=element) for element in elementlist]
    where = "{base} ({elements})".format(base=base, elements=" OR ".join(elements))
    return where


def listdir_fullpath(path):
    return [os.path.join(path, filename) for filename in os.listdir(path)]


def results_to_vega():
    vegaspec = "vegaspec.json"
    template = """<html>
      <head>
        <title>Vega Scaffold</title>
        <script src="http://trifacta.github.io/vega/lib/d3.v3.min.js"></script>
        <script src="http://trifacta.github.io/vega/lib/d3.geo.projection.min.js"></script>
        <script src="http://trifacta.github.io/vega/lib/topojson.js"></script>
        <script src="http://trifacta.github.io/vega/vega.js"></script>
      </head>
      <body>
        <div id="vis"></div>
      </body>
    <script type="text/javascript">
    // parse a spec and create a visualization view
    function parse(spec) {
      vg.parse.spec(spec, function(chart) { chart({el:"#vis"}).update(); });
    }
    parse({
  "width": 400,
  "height": 200,
  "padding": {"top": 10, "left": 30, "bottom": 20, "right": 10},
  "data": [
    {
      "name": "table",
      "values": [
        {"x":"A", "y":28}, {"x":"B", "y":55}, {"x":"C", "y":43},
        {"x":"D", "y":91}, {"x":"E", "y":81}, {"x":"F", "y":53},
        {"x":"G", "y":19}, {"x":"H", "y":87}, {"x":"I", "y":52}
      ]
    }
  ],
  "scales": [
    {"name":"x", "type":"ordinal", "range":"width", "domain":{"data":"table", "field":"data.x"}},
    {"name":"y", "range":"height", "nice":true, "domain":{"data":"table", "field":"data.y"}}
  ],
  "axes": [
    {"type":"x", "scale":"x"},
    {"type":"y", "scale":"y"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data":"table"},
      "properties": {
        "enter": {
          "x": {"scale":"x", "field":"data.x"},
          "width": {"scale":"x", "band":true, "offset":-1},
          "y": {"scale":"y", "field":"data.y"},
          "y2": {"scale":"y", "value":0}
        },
        "update": { "fill": {"value":"steelblue"} },
        "hover": { "fill": {"value":"red"} }
      }
    }
  ]
});
    </script>
    </html>"""
    report = open("result.html", "w+")
    report.write(template)
    report.close()


if __name__ == "__main__": main(sys.argv[1])