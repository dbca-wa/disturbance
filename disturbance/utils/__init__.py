import sys
from datetime import datetime

import pytz
from django.conf import settings
from disturbance.components.proposals.models import Proposal, ProposalType, HelpPage, ApplicationType
from collections import OrderedDict
from copy import deepcopy

def search_all(search_list, application_type='Disturbance'):
    """
    To run:
        from disturbance.utils import search_all
        search_all(['BRM', 'JM 1'])
    """
    result = {}
    for p in Proposal.objects.filter(application_type__name=application_type):
        try:
            if p.data:
                ret = search(p.data[0], search_list)
                if ret:
                    result.update( {p.lodgement_number: ret} )
        except:
            pass

    return result

def search(dictionary, search_list):
    """
    To run:
        from disturbance.utils import search
        search(dictionary, ['BRM', 'JM 1'])
    """
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.items():
        if any(x.lower()==v.lower() for x in search_list):
            result.append( {k: v} )
    return result

def search2(dictionary, search_list):
    """
    To run:
        from disturbance.utils import search2
        search2(p.data, ['BRM', 'JM 1'])
        search2(p.data, search_list=['finalSection.Section8-0', 'tenureSection.Section1-0.Section1-0-3'])
            output:
                {'finalSection.Section8-0': 'yes',
                 'tenureSection.Section1-0.Section1-0-3': 'on'}
    """
    result = {}
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.items():
        for search_item in search_list:
            if k.lower()==search_item.lower():
                result.update( {k: v} )

    return result


def search_approval(approval, searchWords):
    qs=[]
    a = approval
    name = ""
    if a.applicant:
        name = a.applicant.name
    if a.surrender_details:
        try:
            results = search(a.surrender_details, searchWords)
            if results:
                final_results = {}
                for r in results:
                    for key, value in r.items():
                        final_results.update({'key': key, 'value': value})   
                res = {
                    'number': a.lodgement_number,
                    'id': a.id,
                    'type': 'Approval',
                    'applicant': name,
                    'text': final_results,
                    }
                qs.append(res)
        except:
            raise
    if a.suspension_details:
        try:
            results = search(a.suspension_details, searchWords)
            if results:
                final_results = {}
                for r in results:
                    for key, value in r.items():
                        final_results.update({'key': key, 'value': value})
                res = {
                    'number': a.lodgement_number,
                    'id': a.id,
                    'type': 'Approval',
                    'applicant': name,
                    'text': final_results,
                    }
                qs.append(res)
        except:
            raise
    if a.cancellation_details:
        try:
            found = False
            for s in searchWords:
                if s.lower() in a.cancellation_details.lower():
                    found = True
            if found:
                res = {
                    'number': a.lodgement_number,
                    'id': a.id,
                    'type': 'Approval',
                    'applicant': name,
                    'text': a.cancellation_details,
                    }
                qs.append(res)
        except:
            raise
    return qs

def search_compliance(compliance, searchWords):
    qs=[]
    c = compliance
    name = ""
    if c.proposal and c.proposal.applicant:
        name = c.proposal.applicant.name
    if c.text:
        try:
            found = False
            for s in searchWords:
                if s.lower() in c.text.lower():
                    found = True
            if found:
                res = {
                    'number': c.reference,
                    'id': c.id,
                    'type': 'Compliance',
                    'applicant': name,
                    'text': c.text,
                    }
                qs.append(res)
        except:
            raise
    if c.requirement:
        try:
            found = False
            for s in searchWords:
                if s.lower() in c.requirement.requirement.lower():
                    found = True
            if found:
                res = {
                    'number': c.reference,
                    'id': c.id,
                    'type': 'Compliance',
                    'applicant': name,
                    'text': c.requirement.requirement,
                    }
                qs.append(res)
        except:
            raise
    return qs

def search_tenure(proposal):
    """
    Retrieves the tenure names/labels from the check boxes checked, by cross-referencing p.data with p.schema (since checkbox has section_name:'on')
    Requires settings.TENURE_SECTION (eg. 'Section1-0')
    """
    if not  settings.TENURE_SECTION: #'Section1-0'
        return

    section_names = []
    for i in flatten(proposal.data[0]):
        if settings.TENURE_SECTION in i:
            name = i.split('.')[-1]
            res = search_multiple_keys(proposal.data[0], primary_search=name, search_list=['name'])
            if res[0][name]:
                section_names.append(name)


    tenure_str = ''
    s = search_keys(proposal.schema, search_list=['name', 'label'])
    for name in section_names:
        for i in s:
            if name ==  i['name']:
                tenure_str = tenure_str + ', ' + i['label'] if tenure_str else tenure_str + i['label']

    return tenure_str

def test_compare_data():
    p=Proposal.objects.get(id=100)

    dict1=p.data[0]
    dict2=p.previous_application.data[0]
    return compare_data(dict1, dict2, p.schema)


def compare_proposal(current_proposal, prev_proposal_id):
    prev_proposal = Proposal.objects.get(id=prev_proposal_id)
    return compare_data(current_proposal.data[0], prev_proposal.data[0], current_proposal.schema)


def convert_moment_str_to_python_datetime_obj(moment_str):
    """
    This function convert moment-obj-str to python datetime obj
    """
    # Serialized moment obj is supposed to be sent. Which is UTC timezone.
    date_utc = datetime.strptime(moment_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # Add timezone (UTC)
    date_utc = date_utc.replace(tzinfo=pytz.UTC)
    # Convert the timezone to TIME_ZONE
    date_perth = date_utc.astimezone(pytz.timezone(settings.TIME_ZONE))

    return date_perth


def compare_data(dict1, dict2, schema):
    """
    dict1 - most recent data
    dict2 - prev data
    schema - proposal.schema

    To run:
        from disturbance.utils import compare
        compare_data(dict1, dict2, schema)

    eg.
        p=Proposal.objects.get(id=110)
        dict1=p.data[0]
        dict2=p.previous_application.data[0]
        return compare_data(dict1, dict2, p.schema)
    """
    result = []
    flat_dict1 = flatten(dict1)
    flat_dict2 = flatten(dict2)
    for k1, v1 in flat_dict1.items():
        for k2, v2 in flat_dict2.items():
            if k1 ==k2 and v2:
                if v1 != v2:
                    result.append( {k1: [v1, v2]} )
                continue

    # Now find the Question(label) for this section(k1 or k2) and incorporate into the dict result
    new = {}
    #name_map=search_keys2(flatten(schema), search_list=['name', 'label'])
    name_map=search_keys(schema, search_list=['name', 'label'])
    for item in result:
        k = list(item.keys())[0]
        v = item[k]
        section = k.split('.')[-1]
        label = [i['label'] for i in name_map if section in i['name'] ]
        if label:
            new.update( {k: {label[0]: v}} )

    return new


def create_helppage_object(application_type='Disturbance', help_type=HelpPage.HELP_TEXT_EXTERNAL):
    """
    Create a new HelpPage object, with latest help_text/label anchors defined in the latest ProposalType.schema
    """
    try:
        application_type_id = ApplicationType.objects.get(name=application_type).id
    except Exception as e:
        print('application type: {} does not exist, maybe!'.format(application_type, e))

    try:
        help_page = HelpPage.objects.filter(application_type_id=application_type_id, help_type=help_type).latest('version')
        next_version = help_page.version + 1
    except Exception as e:
        next_version = 1

    try:
        proposal_type = ProposalType.objects.filter(name=application_type).latest('version')
    except Exception as e:
        print('proposal type: {} does not exist, maybe!'.format(application_type, e))


    help_text = 'help_text_url' if help_type==HelpPage.HELP_TEXT_EXTERNAL else 'help_text_assessor_url'
    help_list = search_keys(proposal_type.schema, search_list=[help_text,'label'])
    richtext = create_richtext_help(help_list, help_text)

    HelpPage.objects.create(application_type_id=application_type_id, help_type=help_type, version=next_version, content=richtext)

def create_richtext_help(help_list=None, help_text='help_text'):

    # for testing
    #if not help_list:
    #   pt = ProposalType.objects.all()[4]
    #   help_list = search_keys(pt.schema, search_list=['help_text','label'])[:3]

    richtext = u''
    for i in help_list:
        # if i.has_key(help_text) and 'anchor=' in i[help_text]:
        if help_text in i and 'anchor=' in i[help_text]:
            anchor = i[help_text].split("anchor=")[1].split("\"")[0]
            #print anchor, i['label']

            richtext += u'<h1><a id="{0}" name="{0}"> {1} </a></h1><p>&nbsp;</p>'.format(anchor, i['label'])
        else:
            richtext += u'<h1> {} </h1><p>&nbsp;</p>'.format(i['label'])

    return richtext

def search_keys(dictionary, search_list=['help_text', 'label']):
    """
    Return search_list pairs from
     the schema -- given help_text, finds the equiv. label

    To run:
        from disturbance.utils import search_keys
        search_keys(p.schema, search_list=['name', 'label'])
        search_keys2(dictionary, search_list=['help_text', 'label'])
        search_keys2(dictionary, search_list=['name', 'label'])
    """
    search_item1 = search_list[0]
    search_item2 = search_list[1]
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.items():
        if any(x in k for x in search_list):
            result.append( {k: v} )
    help_list = []
    for i in result:
        try: 
            key = list(i.keys())[0]
            if key and key.endswith(search_item1):
                corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.' + search_item2
                for j in result:
                    key_label = list(j.keys())[0]
                    if key_label and key_label.endswith(search_item2) and key_label == corresponding_label_key: # and result.has_key(key):
                        help_list.append({search_item2: j[key_label], search_item1: i[key]})
        except Exception as e:
            print(e)

    return help_list

def get_schema_questions(dictionary):
    '''
    from disturbance.utils import get_schema_questions
    p=Proposal.objects.get(id=1541)
    qlist = get_schema_questions(p.schema)

    '8.10.4 Attach a Road Access Plan (CEM018)' in qlist
    Out[52]: True

    '''
    _dict = search_keys(dictionary, search_list=['name', 'label'])
    return [i['label'] for i in _dict if i['label']]

def search_keys_group(dictionary, search_list=['name', 'label', 'group']):
    """
    Return search_list pairs from
     the schema -- given help_text, finds the equiv. label

    To run:
        from disturbance.utils import search_keys_group
        search_keys_group(p.schema, search_list=['name', 'label', 'group'])
    """
    search_item1 = search_list[0]
    search_item2 = search_list[1]
    search_item3 = search_list[2]
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.items():
        if any(x in k for x in search_list):
            result.append( {k: v} )
    help_list = []
    for i in result:
        try: 
            key = list(i.keys())[0]
            if key and key.endswith(search_item1):
                found_key={}
                found_key.update({search_item1: i[key]})
                if '.' in key:
                    corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.' + search_item2
                    corresponding_group_key = '.'.join(key.split('.')[:-1]) + '.' + search_item3
                else:
                    corresponding_label_key =  search_item2
                    corresponding_group_key =  search_item3
                for j in result:
                    key_label = list(j.keys())[0]
                    if key_label and key_label.endswith(search_item2) and key_label == corresponding_label_key: # and result.has_key(key):
                        found_key.update({search_item2: j[key_label]})
                    if key_label and key_label.endswith(search_item3) and key_label == corresponding_group_key: # and result.has_key(key):
                        found_key.update({search_item3: j[key_label]})
                help_list.append(found_key)
        except Exception as e:
            print(e)
    return help_list

def missing_required_fields(proposal):
    """
    Returns the missing required fields from the schema (no data is entered)
    """
    data = flatten(proposal.data[0])
    sections = search_multiple_keys(proposal.schema, primary_search='isRequired', search_list=['label', 'name'])

    missing_fields = []
    for flat_key in data.items():
        for item in sections:
            if flat_key[0].endswith(item['name']):
                if not flat_key[1].strip():
                   missing_fields.append( dict(name=flat_key[0], label=item['label']) )
    return missing_fields

def test_search_multiple_keys():
    p=Proposal.objects.get(id=139)
    return search_multiple_keys(p.schema, primary_search='isRequired', search_list=['label', 'name'])

def search_multiple_keys(dictionary, primary_search='isRequired', search_list=['label', 'name']):
    """
    Given a primary search key, return a list of key/value pairs corresponding to the same section/level

    To test:
        p=Proposal.objects.get(id=139)
        return search_multiple_keys(p.schema, primary_search='isRequired', search_list=['label', 'name'])

    Example result:
    [
        {'isRequired': {'label': u'Enter the title of this proposal','name': u'Section0-0'}},
        {'isRequired': {'label': u'Enter the purpose of this proposal', 'name': u'Section0-1'}},
        {'isRequired': {'label': u'In which Local Government Authority (LAG) is this proposal located?','name': u'Section0-2'}},
        {'isRequired': {'label': u'Describe where this proposal is located', 'name': u'Section0-3'}}
    ]
    """

    # get a flat list of the schema and keep only items in all_search_list
    all_search_list = [primary_search] + search_list
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.items():
        if any(x in k for x in all_search_list):
            result.append( {k: v} )

    # iterate through the schema and get the search items corresponding to each primary_search item (at the same level/section)
    help_list = []
    for i in result:
        try:
            tmp_dict = {}
            # key = i.keys()[0]
            key = list(i.keys())[0]  # n Python 3 dict.keys() returns an iterable but not indexable object.  Therefore convert it to an iterable, which is list.
            if key and key.endswith(primary_search):
                for item in all_search_list:
                    corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.' + item
                    for j in result:
                        key_label = list(j.keys())[0]
                        if key_label and key_label.endswith(item) and key_label == corresponding_label_key: # and result.has_key(key):
                            tmp_dict.update({item: j[key_label]})
                if tmp_dict:
                    help_list.append(  tmp_dict )
                #if tmp_dict:
                #  help_list.append( {primary_search: tmp_dict} )

        except Exception as e:
            print(e)

    return help_list

def flatten(old_data, new_data=None, parent_key='', sep='.', width=4):
    '''
    Json-style nested dictionary / list flattener
    :old_data: the original data
    :new_data: the result dictionary
    :parent_key: all keys will have this prefix
    :sep: the separator between the keys
    :width: width of the field when converting list indexes
    '''
    if new_data is None:
        #new_data = {}
        new_data = OrderedDict()

    if isinstance(old_data, dict):
        for k, v in old_data.items():
            new_key = parent_key + sep + k if parent_key else k
            flatten(v, new_data, new_key, sep, width)
    elif isinstance(old_data, list):
        if len(old_data) == 1:
            flatten(old_data[0], new_data, parent_key, sep, width)
        else:
            for i, elem in enumerate(old_data):
                new_key = "{}{}{:0>{width}}".format(parent_key, sep if parent_key else '', i, width=width)
                flatten(elem, new_data, new_key, sep, width)
    else:
        if parent_key not in new_data:
            new_data[parent_key] = old_data
        else:
            raise AttributeError("key {} is already used".format(parent_key))

    return new_data

def search_label(schema, label, new_data=None, parent_key='', sep='.', width=4):
    '''
    Return the entire section for a given schema question (label), including any nested questions within that question

    Eg.
        from disturbance.utils import search_section,search_keys, flatten, search_label
        p=Proposal.objects.get(id=1533)
        j, _bool=search_label(p.schema, '4.0.1.1 Specify')

        In [5]: j
        Out[5]: 
        {'name': 'Section3-0-Yes1-15-On-1',
         'type': 'text_area',
         'label': '4.0.1.1 Specify',
         'isRequired': 'true'}
 
    Json-style nested dictionary / list flattener (this is the p.schema)
    :schema: the original data
    :new_data: the result dictionary
    :parent_key: all keys will have this prefix
    :sep: the separator between the keys
    :width: width of the field when converting list indexes

    '''
    if new_data is None:
        new_data = OrderedDict()

    if isinstance(schema, dict):
        for k, v in schema.items():
            if isinstance(schema, dict) and 'label' in schema and schema['label'] == label:
                return [schema], True

            new_key = parent_key + sep + k if parent_key else k
            d, _bool = search_label(v, label, new_data, new_key, sep, width)
            if _bool:
                # recursively return from all re-entrant function calls
                return d, True

    elif isinstance(schema, list):
        if len(schema) == 1:
            d, _bool = search_label(schema[0], label, new_data, parent_key, sep, width)
            if _bool:
                # recursively return from all re-entrant function calls
                return d, True

        else:
            for i, elem in enumerate(schema):
                new_key = "{}{}{:0>{width}}".format(parent_key, sep if parent_key else '', i, width=width)
                d, _bool = search_label(elem, label, new_data, new_key, sep, width)
                if _bool:
                    # recursively return from all re-entrant function calls
                    return d, True
    else:
        if parent_key not in new_data:
            new_data[parent_key] = schema, False
        else:
            raise AttributeError("key {} is already used".format(parent_key))

    return new_data, False


def create_dummy_history(proposal_id):
    p=Proposal.objects.get(id=proposal_id)
    prev_proposal = deepcopy(p)
    p.id=None
    p.data[0]['proposalSummarySection'][0]['Section0-0']='dd 3'
    p.data[0]['proposalSummarySection'][0]['Section0-1']='ee 3'
    p.previous_application = prev_proposal
    p.save()

    prev_proposal = deepcopy(p)
    p.id=None
    p.data[0]['proposalSummarySection'][0]['Section0-0']='dd 44'
    p.data[0]['proposalSummarySection'][0]['Section0-1']='ee 44'
    p.previous_application = prev_proposal
    p.save()
    return p.id, p.get_history


def are_migrations_running():
    '''
    Checks whether the app was launched with the migration-specific params
    '''
    # return sys.argv and ('migrate' in sys.argv or 'makemigrations' in sys.argv)
    return sys.argv and ('migrate' in sys.argv or 'makemigrations' in sys.argv or 'showmigrations' in sys.argv or 'sqlmigrate' in sys.argv)

def search_section(schema, section_label, question, data, answer):
    question_names=[]
    found_fields=[]
    section_label=section_label.replace(" ","")
    question_label=question.question
    question_type=question.answer_type
    for item in schema:
        children=[]
        # question_names=[]
        # found_fields=[]
        # section_label=section_label.replace(" ","")
        # question_label=question.question
        # question_type=question.answer_type

        # if item['type']=='section' and item['name']:
        #     item_name=item['name'].rstrip('0123456789')
        #     print(item_name, section_label)
        #     if item_name==section_label:
        if item['type']=='section' and item['label']:
            item_label=item['label'].replace(" ","")
            if item_label==section_label:
                children=item['children']
                if children:
                    #children_keys= search_keys_group(children, ['name', 'label', 'group'])
                    children_keys= search_keys_group(item, ['name', 'label', 'group'])
                    if children_keys:
                        question_names=[]
                        for key in children_keys:
                            if 'label' in key and key['label']==question_label:
                                if question_type=='checkbox':
                                    for ch in children_keys:
                                        if 'group' in ch and ch['group']==key['name'] and ch['label']==answer:
                                            question_names.append({'name': ch['name'], 'label': ch['label']})
                                else:
                                    question_names.append({'name': key['name'], 'label': key['label']})
                break

    data = flatten(data[0])
    for flat_key in data.items():
        key_name=flat_key[0]
        #if flat_key has numbers at the end e.g. ProposalSummary0.Section0-0.0000, usually for multiselect answers.
        if len(key_name[len(key_name.rstrip('0123456789')):])==4:
            key_name=key_name[:-5]
        for item in question_names:
            # key_name=flat_key[0]
            # #if flat_key has numbers at the end e.g. ProposalSummary0.Section0-0.0000, usually for multiselect answers.
            # if len(key_name[len(key_name.rstrip('0123456789')):])==4:
            #     key_name=key_name[:-5]

            if key_name.endswith(item['name']):
                if flat_key[1].strip():
                    if question_type=='checkbox':
                        if 'on' in flat_key[1]:
                            found_fields.append( dict(key=item['label'], value=flat_key[1]) )
                            break 
                    else: 
                        # if answer.replace(" ","").lower() in flat_key[1].lower():
                        if answer.strip().lower() in flat_key[1].lower():
                            found_fields.append( dict(key=item['label'], value=flat_key[1]) )
                            break
    return found_fields


