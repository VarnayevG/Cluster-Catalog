from data_prep import cwd
import matlab.engine
import os
import re
import shutil
import subprocess


def start_engine():
    eng = matlab.engine.start_matlab()
    return eng


def append_path(foledrs_list, paths_list):
    for folder in foledrs_list:
        os.chdir(folder)
        path = f'{os.getcwd()}/{os.listdir()[0]}'
        paths_list.append(path)
        os.chdir('..')


def get_path_lists(cwd):
    FGM_folders = ('C1_CP_FGM_5VPS', 'C2_CP_FGM_5VPS',
    'C3_CP_FGM_5VPS', 'C4_CP_FGM_5VPS')
    H1_CIS_folders = (
        'C1_CP_CIS-CODIF_HS_H1_MOMENTS',
        'C3_CP_CIS-CODIF_HS_H1_MOMENTS',
        'C4_CP_CIS-CODIF_HS_H1_MOMENTS'
    )
    O1_CIS_folders = (
        'C1_CP_CIS-CODIF_HS_O1_MOMENTS',
        'C3_CP_CIS-CODIF_HS_O1_MOMENTS',
        'C4_CP_CIS-CODIF_HS_O1_MOMENTS'
    )
    os.chdir(cwd)
    FGM_paths, H1_CIS_paths, O1_CIS_paths = [], [], []
    append_path(FGM_folders, FGM_paths)
    append_path(H1_CIS_folders, H1_CIS_paths)
    append_path(O1_CIS_folders, O1_CIS_paths)
    return FGM_paths, H1_CIS_paths, O1_CIS_paths

    
def execute_curlometer(eng, FGM_paths):
    # FGM_folders = ('C1_CP_FGM_5VPS', 'C2_CP_FGM_5VPS',
    # 'C3_CP_FGM_5VPS', 'C4_CP_FGM_5VPS')
    # paths = []
    # for folder in FGM_folders:
    #     os.chdir(folder)
    #     paths.append(f'{os.getcwd()}/{os.listdir()[0]}')
    #     os.chdir('..')
    eng.readandplot(*FGM_paths, nargout=0)


def execute_denseties(eng, FGM_paths, H1_CIS_paths, O1_CIS_paths):
    flags = (1, 3, 4)
    FGM_paths = [path for path in FGM_paths if 'C2' not in path]
    for flag, path1, path2, path3 in zip(flags, FGM_paths, H1_CIS_paths, O1_CIS_paths):
        eng.densities_plotting(flag, path1, path2, path3, nargout=0)


def execute_mva(eng, FGM_paths):
    for path in FGM_paths:
        eng.readdata(path, nargout=0)
    MVA_path = FGM_paths[-1]
    return MVA_path


def execute_spatial(eng, FGM_paths, H1_CIS_paths, MVA_path):
    #C_nums = tuple(i for i in range(1,5))
    for path in H1_CIS_paths:
        if re.findall(r'C\d_CP', MVA_path)[0] in path:
            HIA_path = path
    print('executing normal')
    eng.spatial_shift(*FGM_paths, HIA_path, MVA_path)
    print('executing averaged')
    eng.averaged_spatial_shift(*FGM_paths, HIA_path, MVA_path)


def copy_results():
    for file in os.listdir():
        if file.endswith(".png"):
            bash_command = f'mv {file} ../results/'
            res = subprocess.check_output(bash_command, shell=True)



def main(cwd):
    FGM_paths, H1_CIS_paths, O1_CIS_paths = get_path_lists(cwd)
    eng = start_engine()
    print('executing curlometer')
    execute_curlometer(eng, FGM_paths)
    print('executing denseties')
    execute_denseties(eng, FGM_paths, H1_CIS_paths, O1_CIS_paths)
    print('executing MVA')
    MVA_path = execute_mva(eng, FGM_paths)
    print('executing spatial')
    execute_spatial(eng, FGM_paths, H1_CIS_paths, MVA_path)
    copy_results()
    print('successful')


os.chdir(cwd)
main(cwd)

