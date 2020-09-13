import requests
import re
import subprocess
import os


file_name = 'CS_crossings_2003.txt'


def read_crossings(file_name):
    events_list = []
    with open(file_name, 'r') as f:
        for line in f.readlines()[2:]:
            if line != '\n' and 'not monotonic' not in line and 'no proton data' not in line:
                events_list.append(line)
    return events_list


def get_date(lst, index):
    event = re.findall(r'\d{14}', lst[index])
    return event


def convert_date(date):
    date = list(date)
    date.insert(4, '-')
    date.insert(7, '-')
    date.insert(10, 'T')
    date.insert(13, ':')
    date.insert(16, ':')
    date.insert(19, 'Z')
    return ''.join(date)


def download_data(START_DATE, END_DATE, COOKIE):
    url = 'https://csa.esac.esa.int/csa/aio/product-action'
    query_specs = {'DATASET_ID': ['C1_CP_FGM_5VPS', 'C2_CP_FGM_5VPS', 'C3_CP_FGM_5VPS', 'C4_CP_FGM_5VPS',
                'C1_CP_CIS-CODIF_HS_H1_MOMENTS', 'C3_CP_CIS-CODIF_HS_H1_MOMENTS', 'C3_CP_CIS-CODIF_HS_H1_MOMENTS', 'C4_CP_CIS-CODIF_HS_H1_MOMENTS',
                'C1_CP_CIS-CODIF_HS_O1_MOMENTS', 'C3_CP_CIS-CODIF_HS_O1_MOMENTS', 'C3_CP_CIS-CODIF_HS_H1_MOMENTS', 'C4_CP_CIS-CODIF_HS_O1_MOMENTS'], 
                'START_DATE': START_DATE,
                'END_DATE': END_DATE,
                'DELIVERY_FORMAT': 'CDF',
                'NON_BROWSER': '1',
                #'DELIVERY_INTERVAL': 'hourly',
                'REF_DOC': '1',
                'CSACOOKIE': COOKIE}
    arch_name = f'{START_DATE}-{END_DATE}.tar.gz'
    with open(arch_name, "wb") as file:
        # get request
        response = requests.get(url, params=query_specs)
        # write to file
        file.write(response.content)
    return arch_name


def tar_unzip(file_name, event):
    res = subprocess.check_output(["tar", "-zxf", file_name, '-C', f'./{event[0]}-{event[1]}/data'])


def move_dirs():
    bash_command = 'for dir in *; do mv "$dir"* ../; done'
    res = subprocess.check_output(bash_command, shell=True)


def main():
    with open('esa_cookie.txt', 'r') as f:
        cookie = f.read().strip()
    events_list = read_crossings(file_name)
    event = get_date(events_list, 5)
    try:
        os.makedirs(f'{event[0]}-{event[1]}/data')
        os.makedirs(f'{event[0]}-{event[1]}/results')
    except FileExistsError:
        print('folder already exists')
        os.chdir(f'{event[0]}-{event[1]}/data')
        return os.getcwd()
    start_date, end_date = event
    start_date = convert_date(start_date)
    end_date = convert_date(end_date)
    arch_name = download_data(start_date, end_date, cookie)
    tar_unzip(arch_name, event)
    os.chdir(f'{event[0]}-{event[1]}/data')
    tmp = os.listdir()[0]
    os.chdir(tmp)
    move_dirs()
    os.chdir('..')
    os.rmdir(tmp)
    return os.getcwd()

cwd = main()

# def tar_unzip(filename):
#     res = subprocess.check_output(["tar", "-zxvf", filename])