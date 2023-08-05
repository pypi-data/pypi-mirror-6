"""
.. index:: model map

============================
Random forest on Zoo dataset
============================

Script :download:`rfzoo.py <../../examples/ensemble/rfzoo.py>` builds a model map of Random forest classifier. Use this
model map to explore the ensemble.

Run the scripy with::

  python rfzoo.py -n 1000 .

This will create a model map of random forest with 1000 trees in the current folder.

"""
import argparse
import os
import sys

import Orange
import Orange.orng.orngVizRank as vr
import orangecontrib.modelmaps as mm


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a model map of Random forest on Zoo dataset.')

    parser.add_argument('output_dir', help='output directory')
    parser.add_argument('-n', type=int, default=1000, help='number of trees in the forest')

    args = parser.parse_args()

    build_map = mm.BuildModelMap('zoo', model_limit=args.n, seed=42)
    data = build_map.data()

    models = build_map.build_rf_models(trees=args.n, max_depth=4, min_instances=5)
    representatives = build_map.select_representatives(models, mm.distance_euclidean)

    table = build_map.build_model_data(representatives)
    smx = build_map.build_model_matrix(representatives, mm.distance_euclidean)

    mm.save(os.path.join(args.output_dir, "rf_zoo_{}_{}".format(smx.dim, sys.platform)), smx, table, data)
