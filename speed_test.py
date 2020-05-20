# python script to regulary test internet speed and perform analytics

import math
import os
import time
import statistics as stats
import matplotlib.pyplot as plt
import datetime
from shutil import copyfile

# read in measurement parameters
configFile = open("./config.txt", 'r')

for line in configFile.readlines():
    if line[0] != '#':
        vals = line.split()

configFile.close()

interval = float(vals[0])
measurements = int(vals[1])
repeats = int(vals[2])

def measure():

    # set file paths for data, dump and temp files
    start_time = time.asctime()
    start_time = start_time.replace(' ', '_')
    start_time = start_time.replace(':', '_')
    os.mkdir(start_time)

    # copy config file into output directory
    config_str = os.path.join(start_time, 'config.txt')
    copyfile("./config.txt", config_str)

    out_str = os.path.join(start_time, 'data.txt')
    dump_str = os.path.join(start_time, 'dump.txt')
    temp_str = os.path.join(start_time, 'temp.txt')
    summ_str = os.path.join(start_time, 'summary_stats.txt')

    for loop in range(measurements):

        distances = []
        latencies = []
        downloads = []
        uploads = []

        measurement_time = time.time()
        
        for counter in range(repeats):
            
            os.system("speedtest-cli > " + temp_str)

            distances.append(getServerDistance(temp_str))
            latencies.append(getLatency(temp_str))
            downloads.append(getDownloadSpeed(temp_str))
            uploads.append(getUploadSpeed(temp_str))

            appendDumpFile(temp_str, dump_str)

        mean_dist = sum(distances)/repeats
        mean_latency = sum(latencies)/repeats
        mean_download = sum(downloads)/repeats
        mean_upload = sum(uploads)/repeats

        std_download = stats.stdev(downloads)/math.sqrt(repeats)
        std_upload = stats.stdev(uploads)/math.sqrt(repeats)
        std_latency = stats.stdev(latencies)/math.sqrt(repeats)

        datafile = open(out_str, 'a+')
        format_str = "{0} {1} {2} {3} {4} {5} {6} {7}\n"
        datafile.write(format_str.format(measurement_time, mean_dist, mean_latency, mean_download, mean_upload, std_download, std_upload, std_latency))
        datafile.close()

        time.sleep(interval*60)

    return start_time

def analyse(start_time):

    data_str = os.path.join(start_time, 'data.txt')
    summ_str = os.path.join(start_time, 'summary_stats.txt')
    
    # populate lists with download, upload, time data
    
    downloads = []
    downloads_error = []

    uploads = []
    uploads_error = []

    times = []

    latencies = []
    latencies_error = []

    datafile = open(data_str, 'r')

    for line in datafile.readlines():
        
        data = line.split()

        downloads.append(float(data[3]))
        downloads_error.append(float(data[5]))

        uploads.append(float(data[4]))
        uploads_error.append(float(data[6]))

        latencies.append(float(data[2]))
        latencies_error.append(float(data[7]))

        times.append(float(data[0]))

    datafile.close()
    
    times = [datetime.datetime.fromtimestamp(measurement) for measurement in times]

    plt.errorbar(times, downloads, yerr=downloads_error, label=r"Download Speed")
    plt.errorbar(times, uploads, yerr=uploads_error, label=r"Upload Speed")
    plt.xlabel("Time of Measurement")
    plt.xticks(rotation = (30))
    plt.ylabel(r"Bandwidth $(Mbs^{-1})$")
    plt.title("Variation of Bandwidth Over Time")
    plt.legend()
    bandwidth_str = os.path.join(start_time, 'bandwidth.png')
    plt.savefig(bandwidth_str)

    plt.close()

    plt.errorbar(times, latencies, yerr=latencies_error)
    plt.xlabel("Time of Measurement")
    plt.xticks(rotation = (30))
    plt.ylabel("Latency (ms)")
    plt.title("Variation of Latency Over Time")
    latency_str = os.path.join(start_time, 'latency.png')
    plt.savefig(latency_str)

    # generate summary statistics
    mean_download = sum(downloads)/len(downloads)
    mean_upload = sum(uploads)/len(uploads)
    mean_latency = sum(latencies)/len(latencies)

    download_std = stats.stdev(downloads)
    upload_std = stats.stdev(uploads)
    latency_std = stats.stdev(latencies)

    summFile = open(summ_str, 'w')

    download_str = "Mean Download Speed: {0} Mb/s, Standard Deviation: {1} \n".format(format(mean_download, '.3f'), format(download_std, '.3f'))
    summFile.write(download_str)

    upload_str = "Mean Upload Speed: {0} Mb/s, Standard Deviation: {1} \n".format(format(mean_upload, '.3f'), format(upload_std, '.3f'))
    summFile.write(upload_str)

    latency_str = "Mean Latency: {0} ms, Standard Deviation: {1} \n".format(format(mean_latency, '.1f'), format(latency_std, '.1f'))
    summFile.write(latency_str)

    summFile.close()

def main():
    start_time = measure()
    analyse(start_time)

def getServerDistance(temp_str):
    
    tempFile = open(temp_str, 'r')
    lines = tempFile.readlines()
    start_pos = lines[4].find('[')
    end_pos = lines[4].find(']')
    tempFile.close()

    distance = lines[4][start_pos+1:end_pos-2]

    return float(distance)

def getLatency(temp_str):

    tempFile = open(temp_str, 'r')
    lines = tempFile.readlines()
    start_pos = lines[4].find(':')
    tempFile.close()

    latency = lines[4][start_pos+2:-3]

    return float(latency)

def appendDumpFile(temp_str, dump_str):

    tempFile = open(temp_str, 'r')
    dumpfile = open(dump_str, 'a+')

    for line in tempFile:
        dumpfile.write(line)

    dumpfile.write('\n')
    
    tempFile.close()
    dumpfile.close()

def getDownloadSpeed(temp_str):

    tempFile = open(temp_str, 'r')

    lines = tempFile.readlines()
    start_pos = lines[6].find(':')
    download = lines[6][start_pos+2:-7]

    return float(download)

def getUploadSpeed(temp_str):

    tempFile = open(temp_str, 'r')

    lines = tempFile.readlines()
    start_pos = lines[8].find(':')
    upload = lines[8][start_pos+2:-7]

    return float(upload)

main()
