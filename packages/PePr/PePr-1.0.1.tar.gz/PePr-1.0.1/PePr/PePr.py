#!/usr/bin/env python
''' The main .py file for the PePr pipeline '''

import re
import os
import sys
import time

import logging
# from memory_profiler import memory_usage

import logConfig
import optParser
import fileParser
import shiftSize
import windowSize
import sigTests
import misc
from classDef import Parameters

def main(argv):
    # initialize the logger 
    root_logger = logging.getLogger("")
    debug = root_logger.debug
    info = root_logger.info
    # performing the option parser
    opt = optParser.opt_parser(argv)
    parameter, readData = optParser.process_opt(opt)

#    mem_usage = memory_usage(-1, interval=1, timeout=1)
#    info(" memory usage is %s MB", mem_usage[0])
    # 1. read and parse the data
    t_start = time.time()
    fileParser.parse(readData, parameter.file_format)
    t_end = time.time()
    info(" Time lapse for parsing file: %f", t_end-t_start)
#    mem_usage = memory_usage(-1, interval=1, timeout=1)
#    info(" memory usage is %s MB", mem_usage[0])

    # 2. remove the redundant reads
    if (parameter.remove_redundant):
        readData.remove_redundant_reads()    

    # 3. shiftSize estimation and shifting reads
    t_start = time.time()
    shiftSize.estimate_shift_size(readData, parameter)
    t_end = time.time()
    info(" Time lapse for estimating shift size: %f", t_end-t_start)
    t_start = time.time()
    shiftSize.shift_reads(readData)
    t_end = time.time()
    info(" Time lapse for shifting size: %f", t_end-t_start)
#    mem_usage = memory_usage(-1, interval=1, timeout=1)
#    info(" memory usage is %s MB", mem_usage[0])

    # 3. calculating the normalization constant 
    windowSize.estimate_normalization_constant(readData, parameter)
     
    # 4. windowSize estimation and split reads into windows
    t_start = time.time()
    windowSize.estimate_window_size(readData, parameter)
    info (" The windowSize is %s", parameter.window_size)
    t_end = time.time()
    info(" Time lapse for estimating window size: %f", t_end-t_start)
    t_start = time.time()
    windowSize.separate_exact_by_window(readData, parameter) 
    t_end = time.time()
    info(" Time lapse for seperating window: %f", t_end-t_start)
#    mem_usage = memory_usage(-1, interval=1, timeout=1)
#    info(" memory usage is %s MB", mem_usage[0])

    t_start = time.time()
    # 5. calling peaks
    if parameter.difftest is False:
        swap = False
        peakfilename = parameter.name+"__PePr_peaks.bed"
        sigTests.negative_binomial(readData, peakfilename, swap, parameter)
    else: 
        up_peakfilename = parameter.name+"__PePr_up_peaks.bed"
        swap = False
        sigTests.negative_binomial(readData, up_peakfilename, swap, parameter)
        down_peakfilename = parameter.name+"__PePr_down_peaks.bed"
        swap = True
        sigTests.negative_binomial(readData, down_peakfilename,
                                   swap, parameter)
    t_end = time.time()
    info(" Time lapse for calling peaks: %f", t_end-t_start)
    # 6. Write to a file that record the command and parameters.     
    parameter.write_parameter_to_file() 
 
if __name__ == '__main__':
    try: main(sys.argv)
    except KeyboardInterrupt: 
        print "user interrupted me"
        
        

