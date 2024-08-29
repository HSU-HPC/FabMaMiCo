import glob
import os


def extract_wall_time_from_out_file(filepath):
    with open(filepath, "r") as f:
        txt = f.readlines()
        for line in txt:
            if "Finished all coupling cycles after" in line:
                seconds = line.split('after ')[-1].split(' ')[0]
                return seconds


if __name__ == '__main__':
    dir_prefix = "_".join(os.environ['SLURM_JOB_NAME'].split("_")[:-2])
    files = glob.glob('../' + dir_prefix + '_mamico_run_replica*/*.out')
    runtimes = []
    for f in files:
        walltime = extract_wall_time_from_out_file(f)
        runtimes.append(walltime)
    print(runtimes)
    print(os.getcwd())
    with open('postprocess_results.txt', 'w') as output:
        for runtime in runtimes:
            output.write(runtime + '\n')
