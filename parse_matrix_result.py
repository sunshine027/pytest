"""
    it is run like this: python parse_matrix_result.py -m matrix.csv -l metric_list.csv,
    and we'll get the value for the option in metric_list.csv, and then fill the value into
    metric_list.csv
"""

from optparse import OptionParser
from decimal import Decimal
import csv
import sys

from common_module.odict import OrderedDict
from common_module.color import inred
from common_module.matrix_tool import get_cstate_for_matrix, get_pstate_for_matrix_by_residency, get_ncres_for_matrix, get_interrupt_for_matrix
from common_module.testexception import TestException

def get_metrics_list(metrics_file):
    with open(metrics_file, 'r') as f:
        reader = csv.reader(f)
        metrics_dict = OrderedDict()
        metric_target_dict = OrderedDict()
        # pass title row
        title_row = reader.next()
        if 'metric' in title_row:
            title_index = title_row.index('metric')
        else:
            raise TestException('Error: the title should be metric')
        if 'target' in title_row:
            target_index = title_row.index('target')
        else:
            raise TestException('Error: the title should be target')
        map(lambda row: metrics_dict.setdefault(row[title_index].strip(), ''), reader)
        # return to head of the file
        f.seek(0)
        map(lambda row: metric_target_dict.setdefault(row[title_index].strip(), row[target_index].strip()), reader)
        return (metrics_dict, metric_target_dict)


def get_value_for_metrics_list(matrix_file, metrics_dict):
    with open(matrix_file) as f:
        reader = csv.reader(f)
        for key in metrics_dict:
            value = ''
            if key in ['C0%', 'C1%', 'C2%', 'C3%', 'C4%', 'C5%', 'C6%']:
                new_key = key[:-1].strip()
                value = get_cstate_for_matrix(new_key, reader, f)
            elif key in ['2D and 3D Graphics', 'Video Encode', 'Video Decode', 'GL3', 'ISP']:
                value = get_ncres_for_matrix(key, reader, f)
            elif key.find('Interrupts') != -1:
                # intr_name is like Interrupts_38
                if len(key.split('_')) != 2:
                    raise TestException('Error: Interrupt should be in this format Interrupts_38')
                new_key = key.split('_')[1].strip()
                value = get_interrupt_for_matrix(new_key, reader, f)
            elif key.find('MemBW') != -1:
                pass
            elif key.find('Wakeups') != -1:
                pass
            elif key.find('MHz') != -1:
                # for pstate
                # key is like 200 MHz, and we only need 200, because the value in matrix.csv is like that
                new_key = key[:-3].strip()
                value = get_pstate_for_matrix_by_residency(new_key, reader, f)
            else:
                raise TestException('Error: we can not recognize %s' % key)
            if value == 0:
                value = ''
            metrics_dict[key] = value
        return  metrics_dict 


def fill_metrics_file(metrics_file, metric_result_dict, metric_target_dict):
    with open(metrics_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'target', 'result'])
        [writer.writerow([key, metric_target_dict[key], value]) for key, value in metric_result_dict.iteritems()]


def parse_args():
    usage = "usage: python %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--matrix', dest='matrix', help="matrix output log", default=False)
    parser.add_option('-l', '--metrics', dest='metrics', help="metrics list", default=False)
    options, args = parser.parse_args()
    if (not options.matrix) or (not options.metrics):
        print inred('Error: you should input -m and -l parameter, the usage is as bellow:')
        parser.print_help()
        sys.exit(2)
    else:
        return (options.matrix, options.metrics) 


def main():
    try:
        matrix_file, metrics_file = parse_args()
        metric_result_dict, metric_target_dict = get_metrics_list(metrics_file)
        metric_result_dict = get_value_for_metrics_list(matrix_file, metric_result_dict)
        fill_metrics_file(metrics_file, metric_result_dict, metric_target_dict)
    except TestException, e:
        print inred(e.value)

if __name__ == '__main__':
    main()

   