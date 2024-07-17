#!/usr/bin/env python3

import shutil
import os
from pathlib import Path
import xml.etree.cElementTree as ET
import subprocess
import copy
import xml.dom.minidom
import sys

m_encoding = 'UTF-8'
curMode = 'gcc'

delMode = False
dryRun = True

maxProcessPerNode = 128
mpiPerNode = maxProcessPerNode

N = [2**x for x in range(0,8)] # [1, 2, 4, 8, 16, 32, 64, 128]
suffixes = ['_{}'.format(x) for x in range(1,4)] # ['_1', '_2', '_3']

mdsize = 80
if len(sys.argv) > 1:
    mdsize = int(sys.argv[1])

stackSize = 1
if len(sys.argv) > 2:
    stackSize = int(sys.argv[2])

filterMasterPath = Path('filter_{}.xml'.format(mdsize))
noFilterMasterPath = Path('nofilter_{}.xml'.format(mdsize))

filterXMLString = filterMasterPath.read_text()
filterXMLString = filterXMLString[21:] # clipping <?xml version="1.0"?> from the beginning

noFilterXMLString = noFilterMasterPath.read_text()
noFilterXMLString = noFilterXMLString[21:] # clipping <?xml version="1.0"?> from the beginning

filterXMLString = '<?xml version="1.0"?><temproot>' + filterXMLString + '</temproot>'
filterTree = ET.fromstring(filterXMLString) # read in the xml file

noFilterXMLString = '<?xml version="1.0"?><temproot>' + noFilterXMLString + '</temproot>'
noFilterTree = ET.fromstring(noFilterXMLString) # read in the xml file

ls1MasterPath = 'box{}.xml'.format(mdsize)

for n in N:
    # edit xml files
    curFilterTree = copy.deepcopy(filterTree)
    curNoFilterTree = copy.deepcopy(noFilterTree)

    curFilterTree.find('couette-test/microscopic-solver').set('number-md-simulations', str(n))
    curNoFilterTree.find('couette-test/microscopic-solver').set('number-md-simulations', str(n))

    for suffix in suffixes:
        pathFilter = os.getcwd() + '/filter' + str(n) + suffix # e.g. /home/amartya/filter1_1, /home/amartya/filter1_2, /home/amartya/filter1_3
        pathNoFilter = os.getcwd() + '/multimd' + str(n) + suffix
        
        #make directory
        try: # first remove
            shutil.rmtree(pathFilter)
            shutil.rmtree(pathNoFilter)
            #print("Removed " + path)
        except OSError as e:
            pass
        if delMode:
            continue # skip to next iteration
        Path(pathFilter).mkdir(parents=True, exist_ok=True)

        # copy mamico xml
        with open(pathFilter + '/couette.xml', 'w') as file:
            dom = xml.dom.minidom.parseString(ET.tostring(curFilterTree))
            #xml_string = dom.toprettyxml()
            xml_string = dom.toxml()
            file.write('<?xml version="1.0"?>'+xml_string[xml_string.find('<temproot>')+10:xml_string.find('</temproot>')])
            #part1, part2 = xml_string.split('?>')
            #file.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
        
        #copy ls1 xml
        shutil.copyfile(ls1MasterPath,pathFilter+'/ls1config.xml')
        #write jobscript
        with open(pathFilter + '/job.sh', 'w') as job:
            job.write('#!/bin/bash\n')
            job.write('#PBS -N E_filter_' + str(n) + suffix + ('_stacked' if stackSize > 1 else '') +'\n')
            job.write('#PBS -l select=' + str(n//stackSize) + ':node_type=rome:mpiprocs=' + str(mpiPerNode) + '\n')
            job.write('#PBS -l walltime=03:00:00\n')
            job.write('\n\n')
            if curMode == 'gcc':
                job.write('module load gcc/12.2.0\n')
            else:
                job.write('module load intel/2022.0.0\n')
            job.write('cd ' + pathFilter + '\n')
            job.write('mpiexec -n ' + str(mpiPerNode * n // stackSize) + ' ~/energyRuns/mamico/build/couette > output 2>&1\n')
            job.write('qstat -fx $JOB_ID | grep resources_used\n')

        #run job
        basedir = os.getcwd()
        os.chdir(pathFilter)
        if not dryRun:
            subprocess.run(["qsub", "job.sh"])
        os.chdir(basedir)

        #repeat for nofilter

        Path(pathNoFilter).mkdir(parents=True, exist_ok=True)

        # copy mamico xml
        with open(pathNoFilter + '/couette.xml', 'w') as file:
            dom = xml.dom.minidom.parseString(ET.tostring(curNoFilterTree))
            #xml_string = dom.toprettyxml()
            xml_string = dom.toxml()
            file.write('<?xml version="1.0"?>'+xml_string[xml_string.find('<temproot>')+10:xml_string.find('</temproot>')])
        
        #copy ls1 xml
        shutil.copyfile(ls1MasterPath,pathNoFilter+'/ls1config.xml')
        #write jobscript
        with open(pathNoFilter + '/job.sh', 'w') as job:
            job.write('#!/bin/bash\n')
            job.write('#PBS -N E_mmd_' + str(n) + suffix + ('_stacked' if stackSize > 1 else '') + '\n')
            job.write('#PBS -l select=' + str(n//stackSize) + ':node_type=rome:mpiprocs=' + str(mpiPerNode) + '\n')
            job.write('#PBS -l walltime=03:00:00\n')
            job.write('\n\n')
            if curMode == 'gcc':
                job.write('module load gcc/12.2.0\n')
            else:
                job.write('module load intel/2022.0.0\n')
            job.write('cd ' + pathNoFilter + '\n')
            job.write('mpiexec -n ' + str(mpiPerNode * n // stackSize) + ' ~/energyRuns/mamico/build/couette > output 2>&1\n')
            job.write('qstat -fx $JOB_ID | grep resources_used\n')
        #run job
        basedir = os.getcwd()
        os.chdir(pathNoFilter)
        if not dryRun:
            subprocess.run(["qsub", "job.sh"])
        os.chdir(basedir)