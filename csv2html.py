#!/usr/bin/python

"""
Usage -
%(scriptName)s -f csv_file_name
%(scriptName)s -s

-h from_top:num = Number of lines from the top that should be made header lines (<th> lines).  Default is 0 = zero.
-h ss:search_string = If search_string matches the beginning of a line, the line will be made a header line (<th> line).

-s = Read from stdin.

-l list|string = Read from a Python list of list or a list of csv strings.

csv elements with 'red:' in front of them will be colored red.
csv elements with 'green:' in front of them will be colored green.

   Fields with embedded commas must be double-quoted, not single-quoted:
echo test1,"test2,200",test3 | %(scriptName)s -s  # good

But for stdin, you must quote the quotes to shield them from the shell:
echo test1,\"test2,200\",test3 | %(scriptName)s -s  # good
echo \'test1,"test2,200",test3\' | %(scriptName)s -s  # good

"""

# From: http://www.enigmaticape.com/blog/simple-python-script-for-simple-csv-to-html-table-rows

import sys
import os
import csv
import string
import getopt
import re
import get_csv
import types

#================================================================

scriptName = os.path.basename(sys.argv[0])

def usage():
    print(__doc__ % {'scriptName': scriptName})
    sys.exit(1)

#================================================================

header_ID_string = ''

# list_of_objects =
#    list of lists
# or
#    list of csv strings

def csv2html(list_of_objects, num_header_lines_from_top = 0, header_ID_string = '', justify_cols='L,R'):

    # print "list_of_objects = " + str(list_of_objects)

    table_string = ""
    for row in list_of_objects:
        table_row = ""
        prev_row_element_value = 0
        # if type(row) in types.StringTypes:
        if "class 'str'" in str(type(row)):
            rc, row_list, max_cols = get_csv.get_csv(csv_input_source = 'string', csv_string = row)
            if rc != 0:
                print("ERROR: csv2html() calling get_csv() = " + str(row_list))
                sys.exit(1)
            # print "row_list[0][1] = " + str(row_list[0][1])
            row_list = row_list[0]
        else:
            row_list = row
        # print "row_list 1 = " + str(row_list)

        # print header_ID_string, row_list[0]

        row_is_header = False
        if header_ID_string != '':
            if re.search(header_ID_string, str(row_list[0])):
                row_is_header = True
        # print "row_list 2 = " + str(row_list)
        td_start = '<td>'
        justify_cols_list = justify_cols.split(',')
        index = -1
        for curr_row_element_value in row_list:
            curr_row_element_value = str(curr_row_element_value)
            index += 1
            if index < len(justify_cols_list):
                if justify_cols_list[index] == 'L':
                    td_start = '<td align="left">'
                else:
                    td_start = '<td align="right">'
            # print "curr_row_element_value = " + str(curr_row_element_value)
            if 'red:' in curr_row_element_value:
                curr_row_element_value = curr_row_element_value.replace('red:', '')
                color_start = '<b><font color="red">'
                color_stop  = '</font></b>'
            elif 'green:' in curr_row_element_value:
                curr_row_element_value = curr_row_element_value.replace('green:', '')
                color_start = '<b><font color="green">'
                color_stop  = '</font></b>'
            else:
                color_start = ''
                color_stop  = ''

            # if curr_row_element_value.isdigit() and prev_row_element_value.isdigit():
            #    print "prev, curr = " + str(prev_row_element_value) + "," + str(curr_row_element_value)
            #    diff = int(curr_row_element_value) - int(prev_row_element_value)
            #    print "diff = " + str(diff)
            #    if diff < 0:
            #       print "percent = " + str(int(.10 * float(prev_row_element_value)))
            #       diff = -diff
            #       if diff > int(.10 * float(prev_row_element_value)):
            #          print "red = " + str(curr_row_element_value)
            #          red_start = '<b><font color="red">'
            #          red_stop  = '</font></b>'
            # prev_row_element_value = curr_row_element_value

            if num_header_lines_from_top > 0 or row_is_header == True:
                table_row += '<th>' + color_start + curr_row_element_value + color_stop + "</th>"
            else:
                table_row += td_start + color_start + curr_row_element_value + color_stop + "</td>"

        if table_row != '':
            table_string += "<tr>" + table_row + "</tr>\n"
            num_header_lines_from_top -= 1

    table_string = '<table border="1">\n' + table_string + "</table>\n"
    return 0, table_string

#================================================================

if __name__ == '__main__':

    if len( sys.argv ) < 2 :
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:sh:l:", [])
    except getopt.GetoptError as err:
        usage()

    output_file = ''
    csvfilename = ''
    list_type = ''
    num_header_lines_from_top = 0
    header_ID_string = ''
    input_source = ''
    opt = ''
    for opt, arg in opts:
        if opt == '-h':
            if 'from_top' in arg.split(':')[0]:
                num_header_lines_from_top = int(arg.split(':')[1])
                continue
            if 'ss' in arg.split(':')[0]:
                header_ID_string = arg.split(':')[1]
                continue
        if opt == '-s':
            input_source = 'stdin'
            continue
        if opt == '-f':
            input_source = 'file'
            csvfilename = arg
            continue
        if opt == '-t':
            input_source = 'string'
            continue
        if opt == '-l':  # List test
            input_source = 'list'
            list_type = arg
            continue

    list_of_lists = []
    if input_source == 'list':
        if list_type == 'list':
            # print "list type"
            list_of_lists = [['1','2','3','4'],['5','6','7','8']]
        elif list_type == 'string':
            # print "string type"
            list_of_csv_strings = ['1,2,3,4','5,6,7,8']
            for csv_string in list_of_csv_strings:
                csv_list = csv_string.split(',')
                list_of_lists.append(csv_list)
    elif input_source == 'stdin':
        for row2 in csv.reader(sys.stdin):
            list_of_lists.append(row2)
    elif input_source == 'file':
        if not os.path.exists(csvfilename):
            sys.stderr.write( csvfilename + " not found \n" )
            sys.exit(4)

        # output_file = csvfilename.replace('.csv', '.html')
        output_file = csvfilename + '.html'
        fd = open(output_file, 'w')

        csvfile = open( csvfilename, 'rb')
        list_of_lists = csv.reader( csvfile )
    else:
        print("ERROR: Unexpected input_source = " + input_source)
        sys.exit(1)

    # print input_source

    # # print csvfilename
    # for row in list_of_lists:
    #    print "row = " + str(row)

    rc, results = csv2html(list_of_lists, num_header_lines_from_top)
    if rc != 0:
        print("ERROR: csv2html() error.")
        sys.exit(1)

    if output_file != '':
        fd.write(results)
        fd.close()

    sys.stdout.write( results)
