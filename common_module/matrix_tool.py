"""
    this module is used to get kinds of value from matrix output log like matrix.csv
"""

from common_module.testexception import TestException


def get_cstate_for_matrix(cstate_name, reader, f):
    #cstate_name is like C0, C1
    cstate_value = 0
    f.seek(0)
    for row in reader:
        #delete all space to compare
        new_row = [option.strip() for option in row]
        if cstate_name == 'C0':
            cstate_name = 'C0_C1'
        if cstate_name in new_row:
            name_index = new_row.index(cstate_name)
            #c_state's result is next to it
            cstate_value = new_row[name_index + 1]
            break
    return cstate_value


def get_pstate_for_matrix_by_residency(pstate_value, reader, f):
    #pstate_value is like 200, 400, 1200
    pstate_result = 0
    pstate_start_index = -1
    f.seek(0)
    for row in reader:
        #delete all space to compare
        new_row = [option.strip() for option in row]
        if pstate_start_index == -1:
            # P State indicates to start look up
            if 'P State' in new_row:
                pstate_start_index = new_row.index('P State')
        else:
            # Frequency and Transition means stopping looking up
            if 'Frequency' not in new_row and 'Transition' not in new_row:
                if str(pstate_value) in new_row:
                    #p_state's result is the percentage value
                    pstate_result = new_row[pstate_start_index + 2]
                    break
            else:
                break
    return pstate_result

def get_pstate_for_matrix_by_name(pstate_name, reader, f):
    pstate_value = 0
    f.seek(0)
    for row in reader:
        #delete all space to compare
        new_row = [option.strip() for option in row]
        if pstate_name in new_row:
            name_index = new_row.index(pstate_name)
            #p_state's result is the percentage value
            pstate_value = new_row[name_index + 2]
            break
    return pstate_value


def get_ncres_for_matrix(ncres_tag, reader, f, ncres_name='D0i3'):
    ncres_index = -1
    ncres_value = 0
    f.seek(0)
    for row in reader:
        #delete all space to compare
        new_row = [option.strip() for option in row]
        if ncres_index == -1:
            if ncres_name in new_row:
                ncres_index = new_row.index(ncres_name)
        else:
            if ncres_tag in new_row:
                ncres_value = new_row[ncres_index]
                break
    return ncres_value


def get_interrupt_for_matrix(intr_value, reader, f, duration_text=None):
    interrupt_start_index = -1
    intr_result = 0
    f.seek(0)
    for row in reader:
        #delete all space to compare
        new_row = [option.strip() for option in row]
        if not duration_text:
            if 'Captured for' in new_row:
                duration_text = new_row[new_row.index('Captured for') + 1]
                # duration_text's format is like 10.0032 seconds, and we only need the float number
                duration_text = duration_text[:-7].strip()
        else:
            # interrupt should get irq value, then divide duration, if more than one exist, we should sum them,
            # and use the division value to compare, here we return the division value
            if interrupt_start_index == -1:
                if 'CPU' in new_row and 'Interrupt' in new_row and 'Information' in new_row:
                    interrupt_start_index = new_row.index('CPU')
            else:
                if 'Total' in new_row and 'Interrupt Rate' in new_row:
                    intr_result = round(intr_result, 1)
                    break
                else:
                    if new_row[interrupt_start_index] == intr_value + ':':
                        original_value = new_row[interrupt_start_index + 1]
                        float_value = deal_with_pecentage_symbol(original_value, 'Error: the value of interrupts %s in matrix is wrong' % original_value)
                        intr_result = intr_result + float_value/float(duration_text)
    return intr_result


def deal_with_pecentage_symbol(original_value, error_message):
    try:
        if str(original_value).find('%') != -1:
            dvalue = str(original_value).replace('%', '')
            float_dvalue = float(dvalue) / 100
        else:
            float_dvalue = float(original_value)
        return float_dvalue
    except (ValueError, TypeError), e:
        raise TestException(error_message)