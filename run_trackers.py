import getopt
import numpy as np
from PIL import Image
from config import *
from scripts import *
import sys
sys.path.append("D:\\STUDY\\PAPER2\\CODE\\ACSNet")
from task.run_acsnet import *

def run_trackers(trackers, seqs, evalType, shiftTypeSet):
    tmpRes_path = RESULT_SRC.format('tmp/{0}/'.format(evalType))
    if not os.path.exists(tmpRes_path):
        os.makedirs(tmpRes_path)

    numSeq = len(seqs)
    numTrk = len(trackers)

    trackerResults = dict((t, list()) for t in trackers)
    for idxSeq in range(numSeq):
        s = seqs[idxSeq]

        subSeqs, subAnno = butil.get_sub_seqs(s, 20.0, evalType)

        for idxTrk in range(len(trackers)):
            t = trackers[idxTrk]
            # 解除跟踪目录的限制
            # if not os.path.exists(TRACKER_SRC + t):
            #     print('{0} does not exists'.format(t))
            #     sys.exit(1)
            if not OVERWRITE_RESULT:
                trk_src = os.path.join(RESULT_SRC.format(evalType), t)
                result_src = os.path.join(trk_src, s.name + '.json')
                if os.path.exists(result_src):
                    seqResults = butil.load_seq_result(evalType, t, s.name)
                    trackerResults[t].append(seqResults)
                    continue
            seqResults = []
            seqLen = len(subSeqs)
            for idx in range(seqLen):
                print('{0}_{1}, {2}_{3}:{4}/{5} - {6}'.format(
                    idxTrk + 1, t, idxSeq + 1, s.name, idx + 1, seqLen, evalType))
                rp = tmpRes_path + '_' + t + '_' + str(idx + 1) + '/'
                if SAVE_IMAGE and not os.path.exists(rp):
                    os.makedirs(rp)
                subS = subSeqs[idx]
                subS.name = s.name + '_' + str(idx)

                os.chdir(TRACKER_SRC)# + t) 不需要名称对应
                funcName = 'run_{0}(subS, rp, SAVE_IMAGE)'.format(t)
                # import task.run_acsnet
                try:
                    res = eval(funcName)
                except:
                    print('failed to execute {0} : {1}'.format(
                        t, sys.exc_info()))
                    os.chdir(WORKDIR)
                    break
                os.chdir(WORKDIR)

                if evalType == 'SRE':
                    r = Result(t, s.name, subS.startFrame, subS.endFrame,
                               res['type'], evalType, res['res'], res['fps'], shiftTypeSet[idx])
                else:
                    r = Result(t, s.name, subS.startFrame, subS.endFrame,
                               res['type'], evalType, res['res'], res['fps'], None)
                try:
                    r.tmplsize = res['tmplsize'][0]
                except:
                    pass
                r.refresh_dict()
                seqResults.append(r)
            # end for subseqs
            if SAVE_RESULT:
                butil.save_seq_result(seqResults)

            trackerResults[t].append(seqResults)
        # end for tracker
    # end for allseqs
    return trackerResults