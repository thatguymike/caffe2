from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from hypothesis import given
import numpy as np

from caffe2.python import core, workspace
import caffe2.python.hypothesis_test_util as hu


# TODO(jiayq): make them hypothesis tests for better coverage.
class TestElementwiseBroadcast(hu.HypothesisTestCase):
    @given(**hu.gcs)
    def test_broadcast(self, gc, dc):
        # Set broadcast and no axis, i.e. broadcasting last dimensions.
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(4, 5).astype(np.float32)
        op = core.CreateOperator("Add", ["X", "Y"], "out", broadcast=1)
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(out, X + Y)
        self.assertDeviceChecks(dc, op, [X, Y], [0])

        # broadcasting intermediate dimensions
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(3, 4).astype(np.float32)
        op = core.CreateOperator("Add", ["X", "Y"], "out", broadcast=1, axis=1)
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(out, X + Y[:, :, np.newaxis])
        self.assertDeviceChecks(dc, op, [X, Y], [0])

        # broadcasting the first dimension
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(2).astype(np.float32)
        op = core.CreateOperator("Add", ["X", "Y"], "out", broadcast=1, axis=0)
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(
            out, X + Y[:, np.newaxis, np.newaxis, np.newaxis])
        self.assertDeviceChecks(dc, op, [X, Y], [0])

    @given(**hu.gcs)
    def test_broadcast_scalar(self, gc, dc):
        # broadcasting constant
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(1).astype(np.float32)
        op = core.CreateOperator("Add", ["X", "Y"], "out", broadcast=1)
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(
            out, X + Y)
        self.assertDeviceChecks(dc, op, [X, Y], [0])

        # broadcasting scalar
        X = np.random.rand(1).astype(np.float32)
        Y = np.random.rand(1).astype(np.float32).reshape([])
        op = core.CreateOperator("Add", ["X", "Y"], "out", broadcast=1)
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(
            out, X + Y)
        self.assertDeviceChecks(dc, op, [X, Y], [0])

    @given(**hu.gcs)
    def test_semantic_broadcast(self, gc, dc):
        # NCHW as default
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(3).astype(np.float32)
        op = core.CreateOperator(
            "Add", ["X", "Y"], "out", broadcast=1, axis_str="C")
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(
            out, X + Y[:, np.newaxis, np.newaxis])
        self.assertDeviceChecks(dc, op, [X, Y], [0])

        # NHWC
        X = np.random.rand(2, 3, 4, 5).astype(np.float32)
        Y = np.random.rand(5).astype(np.float32)
        op = core.CreateOperator(
            "Add", ["X", "Y"], "out", broadcast=1, axis_str="C", order="NHWC")
        workspace.FeedBlob("X", X)
        workspace.FeedBlob("Y", Y)
        workspace.RunOperatorOnce(op)
        out = workspace.FetchBlob("out")
        np.testing.assert_array_almost_equal(out, X + Y)
        self.assertDeviceChecks(dc, op, [X, Y], [0])

if __name__ == "__main__":
    import unittest
    unittest.main()
