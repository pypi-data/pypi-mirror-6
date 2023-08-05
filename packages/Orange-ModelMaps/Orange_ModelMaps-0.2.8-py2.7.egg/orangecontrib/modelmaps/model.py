"""
.. index:: model

*****
Model
*****

.. autoclass:: Orange.modelmaps.Model
   :members:

"""
import uuid
import numpy as np

from itertools import groupby
from operator import itemgetter

from Orange import data


class Model(object):

    def __init__(self, type_, classifier, probabilities, \
                 class_values, attributes, \
                 instance_predictions=None, instance_classes=None, \
                 name=None, XAnchors=None, YAnchors=None):
        """Meta-model, a node in Model Map.

        :param type_: model type; must be in MODEL_LIST
        :type type_: string

        :param classifier: classifier object of this model
        :type classifier: :obj:`Orange.classification.Classifier`

        :param probabilities: list of predicted probabilities (for all classes)
        :type probabilities: list of :obj:`numpy.ndarray`

        :param attributes: list of attribute names
        :type attributes: list

        :param instance_predictions: array of predicted classes for all instances
        :type instance_predictions: :obj:`numpy.ndarray`

        :param instance_classes: array of true classes for all instances
        :type instance_classes: :obj:`numpy.ndarray`

        :param name: model name
        :type name: string

        :param XAnchors:
        :type XAnchors: list

        :param YAnchors:
        :type YAnchors: list

        """
        self.uuid = uuid.uuid4().hex
        self.type = type_
        self.classifier = classifier
        self.probabilities = probabilities
        self.class_values = class_values
        self.attributes = attributes
        self.instance_predictions = instance_predictions
        self.instance_classes = instance_classes
        self.name = name if name is not None else self.type
        self.XAnchors = XAnchors
        self.YAnchors = YAnchors
        self.instance = None

    def set_instance(self, instance):
        """Set :obj:`Orange.data.Table` instance with model meta-data."""
        self.instance = instance

    def get_instance(self, domain):
        """Return :obj:`Orange.data.Table` instance with model meta-data.

        :param domain: instance will match given domain
        :type domain: :obj:`Orange.data.Domain`
        """
        if self.instance:
            inst = data.Instance(domain, [v.value for v in self.instance])
            # PyObject not assigned by constructor
            inst['model'] = self.instance['model']
            return inst

        inst = data.Instance(domain)

        inst['uuid'] = self.uuid
        inst['number of attributes'] = len(set(self.attributes))
        results = [p == c for p, c in zip(self.instance_predictions, self.instance_classes)]
        inst['CA'] = sum(results) / float(len(results))
        inst['P'] = np.mean([p[self.class_values[c]] for p, c in zip(self.probabilities, self.instance_classes)])

        classes = zip(*sorted(self.class_values.items(), key=itemgetter(1)))[0]
        outcomes = np.array([c == self.instance_classes for c in classes]).T

        inst['Brier'] = np.sum(np.square(self.probabilities - outcomes)) / len(self.probabilities)
        inst['Brier by class'] = ', '.join(map(str, zip(*sorted(zip(classes, np.sum(np.square(self.probabilities - outcomes), axis=0) / len(self.probabilities))))[1]))
        inst['type'] = self.type
        inst['model'] = self
        inst['attributes'] = ', '.join(self.attributes)

        resultsByClass = sorted([(p == c, c) for p, c in zip(self.instance_predictions, self.instance_classes)], key=itemgetter(1))
        groups = []
        for _k, g in groupby(resultsByClass, lambda x: x[1]):
            resultsByClass, _classes = zip(*g)
            groups.append(resultsByClass)
        inst["CA by class"] = ', '.join([str(sum(results) / float(len(results))) for results in groups])
        inst["label"] = self.name

        return inst
