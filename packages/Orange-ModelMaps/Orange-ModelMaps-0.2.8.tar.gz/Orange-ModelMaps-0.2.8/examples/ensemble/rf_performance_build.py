__author__ = '"Miha Stajdohar" <miha.stajdohar@gmail.com>'

import matplotlib
matplotlib.use('Agg')

import os.path, sys
import numpy as np
import orangecontrib.modelmaps as mm
#import cPickle as pickle

from Orange import data, utils

ROOT = "/home/miha/work/res/modelmaps"
ROOT = "C:\\Users\\Miha\\work\\res\\modelmaps"
#ROOT = "/Network/Servers/xgridcontroller.private/lab/mihas/modelmaps"

def build_rd_map(DATASET):
    fname = os.path.join(utils.environ.dataset_install_dir, "%s%s" % (DATASET, ".tab"))

    if not (os.path.exists(fname) and os.path.isfile(fname)):
        fname = os.path.join(ROOT, "tab", "%s%s" % (DATASET, ".tab"))

        if not (os.path.exists(fname) and os.path.isfile(fname)):
            raise IOError("File %s not found." % fname)

    build_map = mm.BuildModelMap(fname)

    trees = 150

    print "build models..."
    models, models_1, rf_classifier, _ = build_map.build_rf_models(trees=trees, max_depth=None, three_folds=False)

    print "build model data..."
    table = build_map.build_model_data(models)
    table_1 = build_map.build_model_data(models_1)

    print "build matrix..."
    smx = build_map.build_model_matrix(models)
    smx_1 = build_map.build_model_matrix(models_1)
    mm.save(os.path.join(ROOT, "_ensemble_", "rf_%s_%d_tree_base_%s" % (DATASET, len(models), sys.platform)), smx, table, build_map.data())
    mm.save(os.path.join(ROOT, "_ensemble_", "rf_%s_%d_tree_base_%s" % (DATASET, len(models_1), sys.platform)), smx_1, table_1, build_map.data())

#build_rd_map("zoo")
#build_rd_map("marketing")
#build_rd_map("vehicle")
#build_rd_map("iris")
#build_rd_map("voting")

DO = ["iris", "breast-cancer-wisconsin", "voting", "zoo", "mushroom", "adult_sample", "glass", "marketing", "primary-tumor", "vehicle", "wdbc", "dermatology"]
DO = ["marketing"]

for d in DO:
    build_rd_map(d)