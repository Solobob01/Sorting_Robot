import cv2
import os
import sys, getopt
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner

runner = None
MODEL_PATH = 'model.eim'

def getNumberValue(img):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, MODEL_PATH)

    with ImageImpulseRunner(modelfile) as runner:
        outputLabel = -1
        try:
            model_info = runner.init()
            #print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']

            # imread returns images in BGR format, so we need to convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # get_features_from_image also takes a crop direction arguments in case you don't have square images
            features, cropped = runner.get_features_from_image(img)

            res = runner.classify(features)
            maxScore = 0
            if "classification" in res["result"].keys():
                #print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                for label in labels:
                    score = res['result']['classification'][label]
                    if score >= maxScore:
                        maxScore = score
                        outputLabel = label
                    #print('%s: %.2f\t' % (label, score), end='')
                #print('', flush=True)

            elif "bounding_boxes" in res["result"].keys():
                #print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                for bb in res["result"]["bounding_boxes"]:
                    #print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                    cropped = cv2.rectangle(cropped, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)
        finally:
            if (runner):
                runner.stop()
        return outputLabel