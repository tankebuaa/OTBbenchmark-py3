import getopt
import numpy as np
from PIL import Image
from config import *
from scripts import *
from run_trackers import *
from sacred import Experiment


ex = Experiment("OTB benchmark")

@ex.config
def cfg():
    arg_trackers = ['acsnet']
    arg_loadSeqs = 'tb50' # 'All'
    arg_evalTypes = ['OPE']  # ['OPE', 'SRE', 'TRE']

@ex.automain
def main(arg_trackers, arg_loadSeqs, arg_evalTypes):
    if len(arg_trackers) is 0:
        trackers = os.listdir(TRACKER_SRC)
    else:
        trackers = [x.strip() for x in arg_trackers]

    if arg_loadSeqs != 'All' and arg_loadSeqs != 'all' and arg_loadSeqs != 'tb50'\
            and arg_loadSeqs != 'tb100' and arg_loadSeqs != 'cvpr13':
        loadSeqs = [x.strip() for x in arg_loadSeqs]
    else:
        loadSeqs = arg_loadSeqs

    if len (arg_evalTypes) is 0:
        evalTypes = ['OPE', 'SRE', 'TRE']
    else:
        evalTypes = [x.strip() for x in arg_evalTypes]

    seqs = []

    if SETUP_SEQ:
        print('Setup sequences ...')
        butil.setup_seqs(loadSeqs)
    testname = input("Input Test name : ")
    print('Starting benchmark for {0} trackers, evalTypes : {1}'.format(
        len(trackers), evalTypes))
    for evalType in evalTypes:
        seqNames = butil.get_seq_names(loadSeqs)
        seqs = butil.load_seq_configs(seqNames)
        trackerResults = run_trackers(
            trackers, seqs, evalType, shiftTypeSet)
        for tracker in trackers:
            results = trackerResults[tracker]
            if len(results) > 0:
                evalResults, attrList = butil.calc_result(tracker,
                    seqs, results, evalType)
                print("Result of Sequences\t -- '{0}'".format(tracker))
                for seq in seqs:
                    try:
                        print('\t\'{0}\'{1}'.format(
                            seq.name, " "*(12 - len(seq.name)))),
                        print("\taveCoverage : {0:.3f}%".format(
                            sum(seq.aveCoverage)/len(seq.aveCoverage) * 100)),
                        print("\taveErrCenter : {0:.3f}".format(
                            sum(seq.aveErrCenter)/len(seq.aveErrCenter)))
                    except:
                        print('\t\'{0}\'  ERROR!!'.format(seq.name))

                print("Result of attributes\t -- '{0}'".format(tracker))
                for attr in attrList:
                    print("\t\'{0}\'".format(attr.name)),
                    print("\toverlap : {0:02.1f}%".format(attr.overlap)),
                    print("\tfailures : {0:.1f}".format(attr.error))

                if SAVE_RESULT : 
                    butil.save_scores(attrList, testname)