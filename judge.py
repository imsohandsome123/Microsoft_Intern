import pandas as pd
from multiprocessing import Pool
import subprocess
import signal
import time
import os
TLE = 60
roster_df = pd.read_csv('./inputs/classroom_roster.csv')
roster_df['github_username'].fillna('NoGithubAcct', inplace = True)
roster_index = pd.Series(roster_df.index,index=roster_df.github_username.values).to_dict()
log_df = roster_df.loc[:, ['identifier','github_username']]
log_df["make_012"] = 'Pass'
log_df["make_3"] = 'Pass'
log_df["make_4"] = 'Pass'
log_df["results_012"] = 0
log_df["results_sigonce_012"] = 0
log_df["results_sigforever_012"] = 0
log_df["results_3"] = 0
log_df["results_sigonce_3"] = 0
log_df["results_sigforever_3"] = 0
log_df["results_4"] = 0
log_df["results_sigonce_4"] = 0
log_df["results_sigforever_4"] = 0

with open('inputs/testcase.txt' ,'r') as f:
    testcase = f.readlines()
    testcase = [testcase[i].strip().split() for i in range(len(testcase))]

with open('inputs/testcase_1.txt' ,'r') as f:
    testcase_1 = f.readlines()
    testcase_1 = [testcase_1[i].strip().split() for i in range(len(testcase_1))]


temp = open('./outputs/temp.txt','w+')

def gen_answer():
    prog_start_time = time.time()
    print('--------------------')
    print('Start generating answers.')
    directory = 'answer_code'
    cmd = subprocess.Popen(["make"], cwd = directory)
    cmd.wait()
    run_testcase_no_signal(directory)
    run_testcase_signal_once(directory)
    run_testcase_signal_forever(directory)
    print(f'Generation done in {time.time() - prog_start_time:.3f} sec(s).')
    print('--------------------\n') 
    return

def make_program(path):
    if path == '012':
        cp_args = ["cp", "-f","./answer_code/Makefile", "./answer_code/main.c", "./answer_code/threefunctions.c", 'directory']
    elif path == '3':
        cp_args = ["cp", "-f","./answer_code/Makefile", "./answer_code/main.c", "./answer_code/threadutils.h", "./answer_code/scheduler.c", 'directory']
    elif path == '4':
        cp_args = ["cp", "-f","./answer_code/Makefile", "./answer_code/main.c", 'directory']
    else:
        exit()
    prog_start_time = time.time()
    print('--------------------')
    print(f'Start preparing [{path}] programs.')
    for i, p in enumerate(sorted(os.listdir(path))):
        print(f'prepare_{path}: {i}', end = '\r')
        directory = os.path.join(path, p)
        threefunctionso_dir = os.path.join(directory, 'threefunctions.o')   
        main_dir = os.path.join(directory,'main')
        cp_args[-1] = directory
                   
        cmd = subprocess.Popen(["rm", "-f", main_dir, threefunctionso_dir])
        cmd.wait()
        cmd = subprocess.Popen(cp_args)
        cmd.wait()
        cmd = subprocess.Popen(["make"], cwd = directory, stdout = temp, stderr = temp)
        status = cmd.wait()
        if status != 0:
            github_name = p.replace('hw3-pseudothread-', '')
            try:
                log_df.at[roster_index[github_name], f'make_{path}'] = 'Fail'
            except:
                pass 
    print(f'Preparation done in {time.time() - prog_start_time:.3f} sec(s).')
    print('--------------------\n') 
    return

def return_handler(processes, stdouts):
    for p in processes:
        try:
            p.terminate()
        finally:
            p.wait()
    
    for f in stdouts:
        f.flush()
        f.close()       
    return

def run_testcase_no_signal(directory):
    cmd = subprocess.Popen(["mkdir", "-p", "results"],cwd = directory)
    cmd.wait()
    processes = []
    stdouts = []
    
    for i in range(17):
        result_dir = os.path.join(directory, 'results', f'{i}.txt')
        f = open(result_dir, 'w+')
        stdouts.append(f)
    for i, arg in enumerate(testcase):
        try:
            p = subprocess.Popen(arg, cwd = directory, stdout = stdouts[i], stderr = temp)
            processes.append(p)
        except:
            pass
    time.sleep(TLE)
    return_handler(processes, stdouts)
    return

def run_testcase_signal_once(directory):
    cmd = subprocess.Popen(["mkdir", "-p", "results_sigonce"],cwd = directory)
    cmd.wait()
    processes = []
    stdouts = []
    for i in range(13):
        result_dir = os.path.join(directory, 'results_sigonce', f'{i}.txt')
        f = open(result_dir, 'w+')
        stdouts.append(f)
    for i, arg in enumerate(testcase_1):
        try:
            p = subprocess.Popen(arg, cwd = directory, stdout = stdouts[i], stderr = temp)
            processes.append(p)        
        except:
            pass
    time.sleep(0.1)
    for p in processes:
        try:
            p.send_signal(signal.SIGTSTP)
        except:
            pass
    time.sleep(TLE)
    return_handler(processes, stdouts)
    return

def run_testcase_signal_forever(directory):
    cmd = subprocess.Popen(["mkdir", "-p", "results_sigforever"],cwd = directory)
    cmd.wait()
    processes = []
    stdouts = []
    for i in range(13):
        result_dir = os.path.join(directory, 'results_sigforever', f'{i}.txt')
        f = open(result_dir, 'w+')
        stdouts.append(f)
    for i, arg in enumerate(testcase_1):
        try:
            p = subprocess.Popen(arg, cwd = directory, stdout = stdouts[i], stderr = temp)
            processes.append(p)        
        except:
            pass
    time.sleep(0.1)
    end_time = time.time() + TLE
    while time.time() < end_time:
        for p in processes:
            try:
                p.send_signal(signal.SIGTSTP)
            except:
                pass
    return_handler(processes, stdouts)
    return

def score_testcase(directory):
    args = [(17,'results'), (13, 'results_sigonce'), (13, 'results_sigforever')]
    for testcase_no, folder_dir in args:
        summary_dir = os.path.join(directory, folder_dir, 'summary.txt')
        f = open(summary_dir, 'w+')
        for i in range(testcase_no):
            test_dir = os.path.join(directory, folder_dir, f'{i}.txt')
            ans_dir = f'answer_code/{folder_dir}/{i}.txt'
            cmd = subprocess.Popen(["diff", "-q", ans_dir, test_dir], stdout = f)
            cmd.wait()
        f.flush()
        f.close()
    for testcase_no, folder_dir in args:
        summary_dir = os.path.join(directory, folder_dir, 'summary.txt')
        with open(summary_dir, 'r') as f:
            score = testcase_no - len(f.readlines())
        path, p = directory.split('/')
        github_name = p.replace('hw3-pseudothread-', '')
        try:
            log_df.at[roster_index[github_name], f'{folder_dir}_{path}'] = score
        except:
            pass 
    return

def score_testcase_stdout(directory):
    args = [(17,'results'), (13, 'results_sigonce'), (13, 'results_sigforever')]
    for testcase_no, folder_dir in args:
        summary_dir = os.path.join(directory, folder_dir, 'summary.txt')
        f = open(summary_dir, 'w+')
        for i in range(testcase_no):
            test_dir = os.path.join(directory, folder_dir, f'{i}.txt')
            ans_dir = f'answer_code/{folder_dir}/{i}.txt'
            cmd = subprocess.Popen(["diff", "-q", ans_dir, test_dir], stdout = f)
            cmd.wait()
        f.flush()
        f.close()
    for testcase_no, folder_dir in args:
        summary_dir = os.path.join(directory, folder_dir, 'summary.txt')
        with open(summary_dir, 'r') as f:
            score = testcase_no - len(f.readlines())
        print(f'{folder_dir}: {score}')
    return


def run_program(path, job_type):
    prog_start_time = time.time()
    print('--------------------')
    if job_type == 2:
        print(f'Start running [{path}] programs , sending signal forever.')
    elif job_type == 1:
        print(f'Start running [{path}] programs , sending signal once.')
    elif job_type == 0:
        print(f'Start running [{path}] programs without signal.')
    args = []
    for i, p in enumerate(sorted(os.listdir(path))):
        directory = os.path.join(path, p)
        args.append(directory)
    pool = Pool(10)
    if job_type == 2:
        pool.map(run_testcase_signal_forever, args)
    elif job_type == 1:
        pool.map(run_testcase_signal_once, args)
    elif job_type == 0:
        pool.map(run_testcase_no_signal, args)
    print(f'Program done in {time.time() - prog_start_time:.3f} sec(s).')
    print('--------------------\n') 
    return

def score_program(path):
    prog_start_time = time.time()
    print('--------------------')
    print(f'Start scoring [{path}] programs.')
    for i, p in enumerate(sorted(os.listdir(path))):
        print(f'scoring_{path}: {i}', end = '\r')
        directory = os.path.join(path, p)
        score_testcase(directory)
    print(f'Program done in {time.time() - prog_start_time:.3f} sec(s).')
    print('--------------------\n') 
    return

def rejudge(github_name, make = True):
    prog_start_time = time.time()
    print('--------------------')
    print(f'Start rejudging {github_name}.')
    directory = f'hw3-pseudothread-{github_name}'
    directory_012 = os.path.join('012', directory)
    directory_3 = os.path.join('3', directory)
    directory_4 = os.path.join('4', directory)              

    if make:
        for d in [directory_012, directory_3, directory_4]:
            threefunctionso_dir = os.path.join(d, 'threefunctions.o')   
            main_dir = os.path.join(d,'main')
            cmd = subprocess.Popen(["rm", "-f", main_dir, threefunctionso_dir])
            cmd.wait()
            cmd = subprocess.Popen(["make"], cwd = d)
            cmd.wait()

    for d in [directory_012, directory_3, directory_4]:
        run_testcase_no_signal(d)
        run_testcase_signal_once(d)
        run_testcase_signal_forever(d)
        print(f'score of {d}')
        score_testcase_stdout(d)

    print(f'rejudge done in {time.time() - prog_start_time:.3f} sec(s).')

    print('--------------------\n') 
    return

if __name__ == '__main__':
    # gen_answer()
    # make_program('012')
    # make_program('3')
    # make_program('4')
    # run_program('012', 0)
    # run_program('012', 1)
    # run_program('012', 2)
    # score_program('012')
    # run_program('3', 0)
    # run_program('3', 1)
    # run_program('3', 2)
    # score_program('3')
    # run_program('4', 0)
    # run_program('4', 1)
    # run_program('4', 2)
    # score_program('4')
    # rejudge('1011cychien')
    # rejudge('Suirenjiruka0108', False)
    # rejudge('henry326326')
    # rejudge('matdexir')
    # rejudge('nlnlOuO', False)
    # rejudge('B06902098')
    # rejudge('beatriceev')
    # rejudge('gracesilia')
    # rejudge('b08902138')
    # rejudge('hermes926')
    # rejudge('SparkleSouL')
    # rejudge('kimnai862')
    # rejudge('onionlai')
    # rejudge('b04902126')
    # rejudge('Gearlad')
    rejudge('gracetheo')


    # log_df.to_csv('./outputs/log.csv')