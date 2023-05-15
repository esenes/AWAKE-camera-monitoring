'''
@author: esenes
Last modified: 31 Oct 2022
'''
import xmltodict

def load_config(fname, switch_size=24):
    with open(fname) as fh:
        xml_file = fh.read()

    data_content = xmltodict.parse(xml_file)
    gui_data = data_content['setupInfos']['serverInfo']
    config_data = data_content['setupInfos']['camera']

    # checks 
    if len(config_data) > switch_size:
        raise ValueError('Too many cameras for a single switch')
    if any( [int(elem['port']) > switch_size for elem in config_data] ):
        raise ValueError('This port does not exist on the switch')

    return config_data, gui_data

    