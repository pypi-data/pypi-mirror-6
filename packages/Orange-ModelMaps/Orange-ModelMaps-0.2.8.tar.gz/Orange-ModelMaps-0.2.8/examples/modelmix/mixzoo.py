"""
.. index:: model map

========================
Model map on Zoo dataset
========================

Script :download:`mixzoo.py <../../examples/modelmix/mixzoo.py>` builds a model map on 7 kinds of models. 3 are classic classification models:

* Naive Bayes
* k-Nearest Neighbour
* Classification Tree

where Classification Trees are taken from Random forest as proposed by Breinman.
We also include 4 projections in 2-dimensional plane:

* Supervised PCA
* Radviz
* Polyviz
* Scatter plot

Projections are wrapped into k-NN classifiers that predict on projected points. The reason behind is that good
projections are those that separate points well (Leban et al. 2005 and 2006).

Run the scripy with::

  python mixzoo.py -n 500 .

This will create a model map in the current folder.

"""
import argparse
import os
import sys

import Orange
import Orange.orng.orngVizRank as vr
import orangecontrib.modelmaps as mm


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a model map on Zoo dataset.')

    parser.add_argument('output_dir', help='output directory')
    parser.add_argument('-n', type=int, default=500, help='maximum number of models of one model type')

    args = parser.parse_args()

    build_map = mm.BuildModelMap('zoo', folds=10, model_limit=args.n, seed=42)
    data = build_map.data()

    features = mm.get_feature_subsets(data.domain, args.n, seed=42)

    nfeatures = len(data.domain.features)
    max_scatterplots = (nfeatures ** 2 - nfeatures) / 2
    features_scatterplot = mm.get_feature_subsets_scatterplot(data.domain, max_scatterplots)
    final_models = []


    def add(model_builder, feature_sets):
        # build models
        models = [model_builder(features) for features in feature_sets]
        # select representative models from graph clusters
        representatives = build_map.select_representatives(models, mm.distance_euclidean)
        final_models.extend(representatives)


    add(lambda f: build_map.build_projection_model(f, vr.LINEAR_PROJECTION), features)
    add(lambda f: build_map.build_projection_model(f, vr.RADVIZ), features)
    add(lambda f: build_map.build_projection_model(f, vr.POLYVIZ), features)
    add(lambda f: build_map.build_projection_model(f, vr.SCATTERPLOT), features_scatterplot)

    learner = Orange.classification.bayes.NaiveLearner()
    add(lambda f: build_map.build_model(f, learner), features)

    learner = Orange.classification.knn.kNNLearner()
    add(lambda f: build_map.build_model(f, learner), features)

    models = build_map.build_rf_models(trees=args.n, max_depth=4, min_instances=5)
    representatives = build_map.select_representatives(models, mm.distance_euclidean)
    final_models.extend(representatives)

    table = build_map.build_model_data(final_models)
    smx = build_map.build_model_matrix(final_models, mm.distance_euclidean)

    mm.save(os.path.join(args.output_dir, "mix_zoo_{}_{}".format(smx.dim, sys.platform)), smx, table, data)
