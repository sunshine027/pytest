from exception.testexception import TestException
from conf import path
OPERATOR_LIST=['cmp', '>=', 'lt', '=', '>delta', 'approx']
CONCATENATION_STR = '%&' 

# assertor is responsible for comparing, so we transform the actual data to float for comparing
# in test module, if you didn't get value for one item, please set it to empty_value
def assertor(criteria_dict, actual_data_dict, operator_dict, addtional_dict, dev_dict, caseFolderName):
    if actual_data_dict == "noResult":
        return 'case not executed'
    result='pass'
    for key, actural_data in actual_data_dict.iteritems():
        if criteria_dict.has_key(key):
            value = criteria_dict[key]
    #    for key, value in criteria_dict.iteritems():
            if len(key.split(CONCATENATION_STR)) == 2:
                tag_name = key.split(CONCATENATION_STR)[0]
                name_error = ' with name ' + key.split(CONCATENATION_STR)[1] + ' '
            else:
                tag_name = key
                name_error = ''
            operator=operator_dict.get(key, 'no_value')
            if operator == 'no_value':
                raise TestException("Error: no operator value for tag " + str(tag_name) + name_error)
    #        actural_data=actual_data_dict.get(key, 'no_value')
    #        if actural_data == 'no_value':
    #            raise TestException("Error: no actual value for tag " + str(tag_name) + name_error + ", maybe there is something wrong with case profile, or the program.")
            if actural_data == 'empty_value':
                raise TestException("Error: we didn't get value for tag " + str(tag_name) + name_error)
            if actural_data == '':
                actural_data = "NULL"
                print "Criteria: " + str(tag_name) + name_error + ": " + str(value)
                print 'failed on ' + str(tag_name) + name_error + ': ' + str(actural_data)
                result = 'fail'
                continue
            if operator != 'cmp':
                original_value = value
                original_actual_value = actural_data
                value = deal_with_pecentage_symbol(value, 'Error: the text of tag ' + tag_name + name_error + ' should be a number')
                actural_data = deal_with_pecentage_symbol(actural_data, 'Error: the value we got for tag '+ tag_name + name_error +' is not a number')
                if operator == '>=':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(original_value)
                    if actural_data < value:
                        print 'failed on ' + str(tag_name) + name_error+ ':' + str(original_actual_value) + ' >= ' + str(original_value)
                        result = 'fail'
                    else:
                        print "Actual: " + str(tag_name) + name_error+ ": " + str(original_actual_value)
                if operator =='lt':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(original_value)
                    if actural_data > value:
                        print 'failed on ' + str(tag_name) + name_error + ':' + str(original_actual_value) + ' lt '+ str(original_value)
                        result = 'fail'
                    else:
                        print "Actual: " + str(tag_name) + name_error + ": " + str(original_actual_value)
                if operator == '=':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(original_value)
                    if value != actural_data:
                        print 'failed on ' + str(tag_name) + name_error + ':' + str(original_actual_value) + ' == ' + str(original_value)
                        result = 'fail'
                    else:
                        print "Actual: " + str(tag_name) + name_error + ": " + str(original_actual_value)
                if operator == 'approx':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(original_value)
                    dvalue = addtional_dict.get(key, 'no_value')
                    if dvalue == 'no_value':
                        raise TestException("Error: no delta attribute of tag " + str(tag_name) + name_error + "found")
                    dvalue = deal_with_pecentage_symbol(dvalue, 'the value of delta attribute of tag '+ tag_name + name_error + 'should be a number')
                    tv = value - actural_data
                    if abs(tv) > dvalue:
                        print 'failed on ' + str(tag_name) + name_error + ':' + str(original_actual_value) + ' and ' + str(original_value)
                        result = 'fail'
                    else:
                        print "Actual: " + str(tag_name) + name_error + ": " + str(original_actual_value)
                if operator == '>delta':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(original_value)
                    dvalue = addtional_dict.get(key, 'no_value')
                    if dvalue == 'no_value':
                        raise TestException("Error: no value attribute of tag " + str(tag_name) + name_error + " found")
                    dvalue = deal_with_pecentage_symbol(dvalue, 'the value of value attribute of tag ' + tag_name + name_error + ' should be a number')
                    tv = value - actural_data
                    if tv > dvalue:
                        print 'failed on ' + str(tag_name) + name_error + ':' + str(original_actual_value) + ' and ' + str(original_value)
                        result = 'fail'
                    else:
                        print "Actual: " + str(tag_name) + name_error + ": " + str(original_actual_value)
            else:
                if str(actural_data).strip() == 'MPEG-4Visual' and str(value).strip() == 'MPEG-4':
                    print "Criteria: " + str(tag_name) + name_error + ": " + str(value)
                    print "Actual: " + str(tag_name) + name_error + ": " + str(actural_data)
                else:
                    if cmp(str(value).strip().lower(), str(actural_data).strip().lower()):
                        print "Criteria: " + str(tag_name) + name_error + ": " + str(value)
                        print 'failed to match ' + str(tag_name).strip() + name_error + ':' + str(actural_data).strip() + " with the value in criteria:" + str(value).strip()
                        result = 'fail'
                    else:
                        print "Criteria: " + str(tag_name) + name_error + ": " + str(value)
                        print "Actual: " + str(tag_name) + name_error + ": " + str(actural_data)
            if tag_name == "AttribValue":
                if result == 'fail':
                    from tools.client import adbAccessor as accessor
                    cli = accessor(dev_dict)
                    stdout, stderr = cli.execute("ls /data/1.*")
                    flag1 = stdout.find("/data/")
                    flag2 = flag1 + 15
                    logname = stdout[flag1:flag2]
                    cli.download(logname, path.result_path + '/' + caseFolderName)
    return result

# just get the Criteria value without Off, but without any transformation
def get_criteria_dict(criteria_ele):
    """
        the key in every dictionary is the concatenation of tag's name and the name attribute's value with CONCATENATION_STR, because sometimes the tag name is the same, like bellow:
        <p_state name="P[0]" operator=">=">0.00001%</p_state>
        <p_state name="P[1]" operator=">=">0.00001%</p_state>
        <p_state name="P[2]" operator=">=">0.00001%</p_state>
        <p_state name="P[3]" operator=">=">0.00001%</p_state>
        to distinguish every item, we use ths format p_state%&P[0], and if the tag has no name attribute, we just use the tag name as key
    """
    print "\nExecute Data: "
    
    criteria_dict={}
    operator_dict={}
    addtional_dict={}
    off_flag=True
    
    criteria_child_list = list(criteria_ele)
    for child in criteria_child_list:
        ctag=child.tag
        key_value=ctag
        ctext=child.text
        name_value = child.get('name')
        if name_value is None:
            pass
        else:
            if name_value.strip() == '':
                raise TestException("Error: the value of name attribute  with tag %s can't be empty." % ctag)
            else:
                key_value = key_value.strip() + CONCATENATION_STR + name_value.strip()
        if ctext is None or ctext.strip() == '':
            raise TestException("Error: the text of tag named %s can't be empty." % ctag)
        if ctext.strip().lower() != 'off':
            off_flag=False
            ast = child.get('operator')
            if ast is None or ast.strip() == '':
                raise TestException("Error: no operator attribute found with tag %s or no operator value" % ctag)
            if ast not in OPERATOR_LIST:
                raise TestException("Error: the value of operator attribute with tag " + str(key) + 'is wrong ')
            operator_dict[key_value]=ast
            criteria_dict[key_value]=ctext
            if ast =='>delta':
                delta_value=child.get('value')
                if delta_value is None or delta_value.strip() == '':
                    raise TestException("Error: the value attribute can't be empty with tag %s" % ctag)
                addtional_dict[key_value]=delta_value
            elif ast == 'approx':
                approx_delta=child.get('delta')
                if approx_delta is None or approx_delta.strip() == '':
                    raise TestException("Error: the delta attribute can't be empty with tag %s" % ctag)
                addtional_dict[key_value]=approx_delta
    if off_flag:
        print "Criteria: None"
    return criteria_dict, addtional_dict, operator_dict

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