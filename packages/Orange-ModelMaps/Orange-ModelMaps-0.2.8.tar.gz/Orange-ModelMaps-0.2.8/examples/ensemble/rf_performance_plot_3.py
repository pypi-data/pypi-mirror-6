import matplotlib
matplotlib.use('Agg')

import os.path
import cPickle as pickle
import matplotlib.pyplot as plt

from Orange import data, ensemble, evaluation, utils
from Orange.classification.tree import SimpleTreeLearner

ROOT = "/home/miha/work/res/modelmaps"
#ROOT = "C:\\Users\\Miha\\work\\res\\modelmaps"
#ROOT = "/Network/Servers/xgridcontroller.private/lab/mihas/modelmaps"

class SimpleTreeLearnerSetProb():
    """
    Orange.classification.tree.SimpleTreeLearner which sets the skip_prob
    so that on average a square root of the attributes will be
    randomly choosen for each split.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, examples, weight=0):
        self.wrapped.skip_prob = 1-len(examples.domain.attributes)**0.5/len(examples.domain.attributes)
        return self.wrapped(examples)

def pickle_scores(DATASET, a=0, b=50, step=1, depth=2, min_instances=5):
    print "Building trees:", DATASET
    fname = os.path.join(utils.environ.dataset_install_dir, "%s%s" % (DATASET, ".tab"))

    if not (os.path.exists(fname) and os.path.isfile(fname)):
        fname = os.path.join(ROOT, "tab", "%s%s" % (DATASET, ".tab"))

        if not (os.path.exists(fname) and os.path.isfile(fname)):
            raise IOError("File %s not found." % fname)

    dataset = data.Table(fname)

    indices = data.sample.SubsetIndices2(p0=0.5, stratified=data.sample.SubsetIndices.Stratified, randseed=42)(dataset)
    train = dataset.select(indices, 0)
    test = dataset.select(indices, 1)

    cas = []
    aucs = []
    briers = []

    for trees in range(a, b, step):
        # uses gain ratio
        #tree = SimpleTreeLearnerSetProb(SimpleTreeLearner(max_depth=depth, min_instances=min_instances))
        #rf_learner = ensemble.forest.RandomForestLearner(learner=tree, trees=trees, name="RF: %d trees; max depth: %d; min instances: %d" % (trees, depth, min_instances))
        rf_learner = ensemble.forest.RandomForestLearner(trees=trees, name="RF: %d trees; max depth: None; min instances: %d" % (trees, min_instances))
        #rf_classifier = rf_learner(train)

        learners = [rf_learner]

        results = evaluation.testing.learn_and_test_on_test_data(learners, train ,test)

        cas.append(evaluation.scoring.CA(results)[0])
        aucs.append(evaluation.scoring.AUC(results)[0])
        briers.append(evaluation.scoring.Brier_score(results)[0])

        #print "%d, %-8s %5.6f  %5.6f  %5.6f" % (trees, learners[0].name, cas[-1], aucs[-1], briers[-1])

    pickle.dump((cas, aucs, briers), open(os.path.join(ROOT, "_ensemble_", "scores_%s_%d_to_%d_depth_%s_instances_%d.pkl" % (DATASET, a, b, depth, min_instances)), "wb"), -1)

pickle_scores("zoo", a=2, b=300, depth=None)
pickle_scores("marketing", a=2, b=300, depth=None)
pickle_scores("vehicle", a=2, b=300, depth=None)
pickle_scores("iris", a=2, b=300, depth=None)
pickle_scores("voting", a=2, b=300, depth=None)

def plot_auc(DATASET, a=2, b=500, depth=2, min_instances=5):
    print "Drawing plots:", DATASET
    cas, aucs, briers = pickle.load(open(os.path.join(ROOT, "_ensemble_", "scores_%s_%d_to_%d_depth_%s_instances_%d.pkl" % (DATASET, a, b, depth, min_instances)), "rb"))

    fig = plt.figure(figsize=(3, 6), dpi=300)
    fig.subplots_adjust(wspace=0.3, hspace=0.6, top=0.9, bottom=0.05, left=0.1, right=0.95)

    ax = fig.add_subplot(3, 1, 1)

    ax.plot(range(len(aucs)), aucs, '-')

    ax.set_xlabel('trees')
    ax.set_ylabel('AUC')
    ax.set_title('RF: %s' % DATASET)

    ax = fig.add_subplot(3, 1, 2)

    ax.plot(range(len(cas)), cas, '-')

    ax.set_xlabel('trees')
    ax.set_ylabel('CA')
    ax.set_title('RF: %s' % DATASET)

    ax = fig.add_subplot(3, 1, 3)

    ax.plot(range(len(briers)), briers, '-')

    ax.set_xlabel('trees')
    ax.set_ylabel('Brier')
    ax.set_title('RF: %s' % DATASET)

    fig.savefig(os.path.join(ROOT, "_ensemble_", "scores_%s_%d_to_%d_depth_%s.png" % (DATASET, a, b, depth)))

plot_auc("zoo", a=2, b=300, depth=None)
plot_auc("marketing", a=2, b=300, depth=None)
plot_auc("vehicle", a=2, b=300, depth=None)
plot_auc("iris", a=2, b=300, depth=None)
plot_auc("voting", a=2, b=300, depth=None)