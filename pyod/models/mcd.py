# -*- coding: utf-8 -*-
"""Outlier Detection with Minimum Covariance Determinant (MCD)
"""
# Author: Yue Zhao <yuezhao@cs.toronto.edu>
# License: BSD 2 clause

from __future__ import division
from __future__ import print_function

from sklearn.covariance import MinCovDet
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.validation import check_array

from .base import BaseDetector

__all__ = ['MCD']


class MCD(BaseDetector):
    """An object for detecting outliers in a Gaussian distributed dataset using
    Minimum Covariance Determinant (MCD): robust estimator of covariance.

    The Minimum Covariance Determinant covariance estimator is to be applied
    on Gaussian-distributed data, but could still be relevant on data
    drawn from a unimodal, symmetric distribution. It is not meant to be used
    with multi-modal data (the algorithm used to fit a MinCovDet object is
    likely to fail in such a case).
    One should consider projection pursuit methods to deal with multi-modal
    datasets.

    First fit a minimum covariance determinant model and then compute the
    Mahalanobis distance as the outlier degree of the data

    See :cite:`rousseeuw1999fast,hardin2004outlier` for details.

    :param contamination: The amount of contamination of the data set,
        i.e. the proportion of outliers in the data set. Used when fitting to
        define the threshold on the decision function.
    :type contamination: float in (0., 0.5), optional (default=0.1)

    :param store_precision: Specify if the estimated precision is stored.
    :type store_precision: bool, optional (default=True)

    :param assume_centered:  If True, the support of the robust location and
        the covariance estimates is computed, and a covariance estimate is
        recomputed from it, without centering the data.
        Useful to work with data whose mean is significantly equal to
        zero but is not exactly zero.
        If False, the robust location and covariance are directly computed
        with the FastMCD algorithm without additional treatment.
    :type assume_centered: bool, optional (default=False)

    :param support_fraction: The proportion of points to be included in the
        support of the raw MCD estimate. Default is None, which implies that
        the minimum value of support_fraction will be used within the
        algorithm: [n_sample + n_features + 1] / 2
    :type support_fraction: float, optional (default=None)

    :param random_state: If int, random_state is the seed used by the random
        number generator; If RandomState instance, random_state is the random
        number generator; If None, the random number generator is the
        RandomState instance used by `np.random`.
    :type random_state: int, RandomState instance or None, optional
        (default=None)

    :var raw_location\_: The raw robust estimated location before correction
        and re-weighting.
    :vartype raw_location\_: array-like of shape (n_features,)

    :var raw_covariance\_: The raw robust estimated covariance before
        correction and re-weighting.
    :vartype raw_covariance\_: array-like of shape (n_features, n_features)

    :var raw_support\_: A mask of the observations that have been used to
        compute the raw robust estimates of location and shape, before
        correction and re-weighting.
    :vartype raw_support\_: array-like of shape (n_samples,)

    :var location\_: Estimated robust location
    :vartype location\_: array-like of shape (n_features,)

    :var covariance\_: Estimated robust covariance matrix
    :vartype covariance\_: array-like of shape (n_features, n_features)

    :var precision\_: Estimated pseudo inverse matrix.
        (stored only if store_precision is True)
    :vartype precision\_: array-like of shape (n_features, n_features)

    :var support\_: A mask of the observations that have been used to compute
        the robust estimates of location and shape.
    :vartype support\_: array-like of shape (n_samples,)

    :var decision_scores\_: The outlier scores of the training data.
        The higher, the more abnormal. Outliers tend to have higher
        scores. This value is available once the detector is
        fitted.
    :vartype decision_scores\_: numpy array of shape (n_samples,)

    :var threshold\_: The threshold is based on ``contamination``. It is the
        ``n_samples * contamination`` most abnormal samples in
        ``decision_scores_``. The threshold is calculated for generating
        binary outlier labels.
    :vartype threshold\_: float

    :var labels\_: The binary labels of the training data. 0 stands for inliers
        and 1 for outliers/anomalies. It is generated by applying
        ``threshold_`` on ``decision_scores_``.
    :vartype labels\_: int, either 0 or 1
    """

    def __init__(self, contamination=0.1, store_precision=True,
                 assume_centered=False, support_fraction=None,
                 random_state=None):
        super(MCD, self).__init__(contamination=contamination)
        self.store_precision = store_precision
        self.assume_centered = assume_centered
        self.support_fraction = support_fraction
        self.random_state = random_state

    # noinspection PyIncorrectDocstring
    def fit(self, X, y=None):
        """Fit the model using X as training data.

        :param X: Training data. If array or matrix,
            shape [n_samples, n_features],
            or [n_samples, n_samples] if metric='precomputed'.
        :type X: {array-like, sparse matrix, BallTree, KDTree}

        :return: self
        :rtype: object
        """
        # Validate inputs X and y (optional)
        X = check_array(X)
        self._set_n_classes(y)

        self.detector_ = MinCovDet(store_precision=self.store_precision,
                                   assume_centered=self.assume_centered,
                                   support_fraction=self.support_fraction,
                                   random_state=self.random_state)
        self.detector_.fit(X=X, y=y)

        # Use mahalanabis distance as the outlier score
        self.decision_scores_ = self.detector_.dist_
        self._process_decision_scores()
        return self

    def decision_function(self, X):
        check_is_fitted(self, ['decision_scores_', 'threshold_', 'labels_'])
        X = check_array(X)

        # Computer mahalanobis distance of the samples
        return self.detector_.mahalanobis(X)

    @property
    def raw_location_(self):
        """The raw robust estimated location before correction and
        re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_location_

    @property
    def raw_covariance_(self):
        """The raw robust estimated location before correction and
        re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_covariance_

    @property
    def raw_support_(self):
        """A mask of the observations that have been used to compute
        the raw robust estimates of location and shape, before correction
        and re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_support_

    @property
    def location_(self):
        """Estimated robust location.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.location_

    @property
    def covariance_(self):
        """Estimated robust covariance matrix.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.covariance_

    @property
    def precision_(self):
        """ Estimated pseudo inverse matrix.
        (stored only if store_precision is True)

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.precision_

    @property
    def support_(self):
        """A mask of the observations that have been used to compute
        the robust estimates of location and shape.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.support_