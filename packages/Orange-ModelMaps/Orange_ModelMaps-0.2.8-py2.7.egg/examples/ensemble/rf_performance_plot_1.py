import matplotlib
matplotlib.use('Agg')

import os.path, random, re, sys
import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np

from itertools import groupby
from operator import itemgetter

from Orange import clustering, distance, evaluation, utils

import orangecontrib.modelmaps as mm

ROOT = "/home/miha/work/res/modelmaps"
ROOT = "C:\\Users\\Miha\\work\\res\\modelmaps"
ROOT = "/Network/Servers/xgridcontroller.private/lab/mihas/modelmaps"

scores = {}
cache = {}

NTREES = 1000
MAXCLUSTERS = 120
EXPMARKER = "1000_120_2fold_tree_base"

def plot_scores(DATASET):
    print "drawing plots..."
    fig = plt.figure(figsize=(6, 8), dpi=300)
    fig.subplots_adjust(wspace=0.0, hspace=0.6, top=0.95, bottom=0.06, left=0.1, right=0.97)

    def add_scores_plot(i, type):

        ax = fig.add_subplot(3, 1, i)

        scores[DATASET][type].sort()
        x, y = [], []
        for k, g in groupby(scores[DATASET][type], key=itemgetter(0)):
            i, s = zip(*list(g))
            x.append(i[0])
            y.append(sum(s) / len(s))

        ax.plot(x, y, '-', color='k', linewidth=1)

        scores[DATASET][type + "_mm"].sort()
        x, y = [], []
        for k, g in groupby(scores[DATASET][type + "_mm"], key=itemgetter(0)):
            i, s = zip(*list(g))
            x.append(i[0])
            y.append(sum(s) / len(s))

        ax.plot(x, y, '--', color='g', linewidth=0.5)

        for label in ax.get_xticklabels():
            label.set_fontsize('small')

        for label in ax.get_yticklabels():
            label.set_fontsize('small')

        ax.set_ybound(0., 1.)

        ax.set_xlabel('trees')
        ax.set_ylabel(type.upper())
        subtitle = " ".join([s[0].upper() + s[1:].lower() for s in re.split("_|-", DATASET) if s != "sample"])
        ax.set_title('%s' % subtitle, weight='bold')

    add_scores_plot(0, "ca")
    add_scores_plot(1, "auc")
    add_scores_plot(2, "brier")

    fig.savefig(os.path.join(ROOT, "_ensemble_", "scores_%s_%s.png" % (EXPMARKER, DATASET)))


def score_trees(rf_classifier, trees, test, DATASET, cluster_indices=None):

    score = scores.get(DATASET, {"ca": [], "auc": [], "brier": [], "ca_mm": [], "auc_mm": [], "brier_mm": []})

    if cluster_indices is None:
        models = [random.sample(trees, i) for i in range(2, min(MAXCLUSTERS * 2, len(trees)))]
    else:
        models = [[trees[random.choice(cluster)] for cluster in clustering] for clustering in cluster_indices]

    for trees in models:
        rf_classifier.classifiers = trees
        classifiers = [rf_classifier]

        test_results = evaluation.testing.ExperimentResults(1,
            classifier_names = ["RF"],
            domain=test.domain,
            test_type = evaluation.testing.TEST_TYPE_SINGLE,
            weights=0)

        test_results.results = [test_results.create_tested_example(0, example) for j, example in enumerate(test)]

        results = evaluation.testing._default_evaluation._test_on_data(classifiers, test)

        for example, classifier, result in results:
            test_results.results[example].set_result(classifier, *result)

        score["ca_mm" if cluster_indices else "ca"].append((len(trees), evaluation.scoring.CA(test_results)[0]))
        score["auc_mm" if cluster_indices else "auc"].append((len(trees), evaluation.scoring.AUC(test_results)[0]))
        score["brier_mm" if cluster_indices else "brier"].append((len(trees), evaluation.scoring.Brier_score(test_results)[0]))

    scores[DATASET] = score

def plot_trees_score(DATASET, depth=None, seed=0):

    print "DATASET:", DATASET

    if not DATASET in cache:
        fname = os.path.join(utils.environ.dataset_install_dir, "%s%s" % (DATASET, ".tab"))

        if not (os.path.exists(fname) and os.path.isfile(fname)):
            fname = os.path.join(ROOT, "tab", "%s%s" % (DATASET, ".tab"))

            if not (os.path.exists(fname) and os.path.isfile(fname)):
                raise IOError("File %s not found." % fname)

        build_map = mm.BuildModelMap(fname)

        print "build models..."
        models, rf_classifier, test = build_map.build_rf_models(trees=NTREES, max_depth=depth, three_folds=False)

        print "build model data..."
        table = build_map.build_model_data(models)

        #print "build matrix..."
        #smx = build_map.build_model_matrix(models)

        class ModelDistanceConstructor(distance.DistanceConstructor):

            def __new__(cls, data=None):
                self = distance.DistanceConstructor.__new__(cls)
                return self.__call__(data) if data else self

            def __call__(self, table):
                return ModelDistance()

        class ModelDistance(distance.Distance):
            def __call__(self, e1, e2):
                return mm.distance_manhattan(e1["model"].value, e2["model"].value)

        def data_center(table, original=table):
            if len(table) == 0:
                print "e",
                sys.stdout.flush()
                table = original
            onemodel = table[0]["model"].value
            model = mm.Model("RF", None,
                np.mean(np.array([ex["model"].value.probabilities for ex in table]), axis=0),
                onemodel.class_values, [],
                [onemodel.class_values.keys()[0]] * len(onemodel.instance_predictions),
                [onemodel.class_values.keys()[0]] * len(onemodel.instance_classes))

            return model.get_instance(table.domain)

        table.random_generator = seed
        clustering.kmeans.data_center = data_center

        table.shuffle()
        cluster_indices = []

        print "kmeans..."
        for c in range(2, MAXCLUSTERS + 1):
            print c,
            sys.stdout.flush()
            kmeans = clustering.kmeans.Clustering(table, centroids=c, distance=ModelDistanceConstructor, initialization=clustering.kmeans.init_diversity)
            clusters_ = sorted(zip(kmeans.clusters, range(len(kmeans.clusters))), key=itemgetter(0))

            cluster_indices_tmp = []
            for k, g in groupby(clusters_, key=itemgetter(0)):
                _, indices = zip(*list(g))
                cluster_indices_tmp.append(indices)

            cluster_indices.append(cluster_indices_tmp)

        trees = [ex["model"].value.classifier for ex in table]

        cache[DATASET] = {}
        cache[DATASET]["rf"] = rf_classifier
        cache[DATASET]["trees"] = trees
        cache[DATASET]["test"] = test
        cache[DATASET]["cluster_indices"] = cluster_indices
    else:
        rf_classifier = cache[DATASET]["rf"]
        trees = cache[DATASET]["trees"]
        test = cache[DATASET]["test"]
        cluster_indices = cache[DATASET]["cluster_indices"]

    print "score trees in RF..."
    score_trees(rf_classifier, trees, test, DATASET)

    print "score trees in MM..."
    score_trees(rf_classifier, trees, test, DATASET, cluster_indices)

    print "pickle scores...",
    sys.stdout.flush()
    pickle.dump(scores, open(os.path.join(ROOT, "_ensemble_", "scores_%s_%s.pkl" % (EXPMARKER, DATASET)), "wb"), -1)
    print "done"

    #plot_scores(DATASET)


if __name__ == "__main__":
    DO = sys.argv[1:]

    if len(DO) == 0:
        DO = ["breast-cancer-wisconsin", "voting", "zoo", "mushroom", "adult_sample", "glass", "primary-tumor", "vehicle", "wdbc", "dermatology", "iris", "marketing"]
        DO = ["breast-cancer-wisconsin", "iris"]

    for i in range(500):
        print i
        for d in DO:
            plot_trees_score(d)