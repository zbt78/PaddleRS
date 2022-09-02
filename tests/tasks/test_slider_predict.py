# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path as osp
import tempfile

import paddlers as pdrs
import paddlers.transforms as T
from testing_utils import CommonTest


class TestSegSliderPredict(CommonTest):
    def setUp(self):
        self.model = pdrs.tasks.seg.UNet(in_channels=10)
        self.transforms = T.Compose([
            T.DecodeImg(), T.Normalize([0.5] * 10, [0.5] * 10),
            T.ArrangeSegmenter('test')
        ])
        self.image_path = "data/ssst/multispectral.tif"
        self.basename = osp.basename(self.image_path)

    def test_blocksize_and_overlap_whole(self):
        # Original image size (256, 256)
        with tempfile.TemporaryDirectory() as td:
            # Whole-image inference using predict()
            pred_whole = self.model.predict(self.image_path, self.transforms)
            pred_whole = pred_whole['label_map']

            # Whole-image inference using slider_predict()
            save_dir = osp.join(td, 'pred1')
            self.model.slider_predict(self.image_path, save_dir, 256, 0,
                                      self.transforms)
            pred1 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred1.shape, pred_whole.shape)

            # `block_size` == `overlap`
            save_dir = osp.join(td, 'pred2')
            with self.assertRaises(ValueError):
                self.model.slider_predict(self.image_path, save_dir, 128, 128,
                                          self.transforms)

            # `block_size` is a tuple
            save_dir = osp.join(td, 'pred3')
            self.model.slider_predict(self.image_path, save_dir, (128, 32), 0,
                                      self.transforms)
            pred3 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred3.shape, pred_whole.shape)

            # `block_size` and `overlap` are both tuples
            save_dir = osp.join(td, 'pred4')
            self.model.slider_predict(self.image_path, save_dir, (128, 100),
                                      (10, 5), self.transforms)
            pred4 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred4.shape, pred_whole.shape)

            # `block_size` larger than image size
            save_dir = osp.join(td, 'pred5')
            self.model.slider_predict(self.image_path, save_dir, 512, 0,
                                      self.transforms)
            pred5 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred5.shape, pred_whole.shape)

    def test_merge_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            # Whole-image inference using predict()
            pred_whole = self.model.predict(self.image_path, self.transforms)
            pred_whole = pred_whole['label_map']

            # 'keep_first'
            save_dir = osp.join(td, 'keep_first')
            self.model.slider_predict(
                self.image_path,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='keep_first')
            pred_keepfirst = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_keepfirst.shape, pred_whole.shape)

            # 'keep_last'
            save_dir = osp.join(td, 'keep_last')
            self.model.slider_predict(
                self.image_path,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='keep_last')
            pred_keeplast = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_keeplast.shape, pred_whole.shape)

            # 'vote'
            save_dir = osp.join(td, 'vote')
            self.model.slider_predict(
                self.image_path,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='vote')
            pred_vote = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_vote.shape, pred_whole.shape)

    def test_geo_info(self):
        with tempfile.TemporaryDirectory() as td:
            _, geo_info_in = T.decode_image(self.image_path, read_geo_info=True)
            self.model.slider_predict(self.image_path, td, 128, 0,
                                      self.transforms)
            _, geo_info_out = T.decode_image(
                osp.join(td, self.basename), read_geo_info=True)
            self.assertEqual(geo_info_out['geo_trans'],
                             geo_info_in['geo_trans'])
            self.assertEqual(geo_info_out['geo_proj'], geo_info_in['geo_proj'])


class TestCDSliderPredict(CommonTest):
    def setUp(self):
        self.model = pdrs.tasks.cd.BIT(in_channels=10)
        self.transforms = T.Compose([
            T.DecodeImg(), T.Normalize([0.5] * 10, [0.5] * 10),
            T.ArrangeChangeDetector('test')
        ])
        self.image_paths = ("data/ssmt/multispectral_t1.tif",
                            "data/ssmt/multispectral_t2.tif")
        self.basename = osp.basename(self.image_paths[0])

    def test_blocksize_and_overlap_whole(self):
        # Original image size (256, 256)
        with tempfile.TemporaryDirectory() as td:
            # Whole-image inference using predict()
            pred_whole = self.model.predict(self.image_paths, self.transforms)
            pred_whole = pred_whole['label_map']

            # Whole-image inference using slider_predict()
            save_dir = osp.join(td, 'pred1')
            self.model.slider_predict(self.image_paths, save_dir, 256, 0,
                                      self.transforms)
            pred1 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred1.shape, pred_whole.shape)

            # `block_size` == `overlap`
            save_dir = osp.join(td, 'pred2')
            with self.assertRaises(ValueError):
                self.model.slider_predict(self.image_paths, save_dir, 128, 128,
                                          self.transforms)

            # `block_size` is a tuple
            save_dir = osp.join(td, 'pred3')
            self.model.slider_predict(self.image_paths, save_dir, (128, 32), 0,
                                      self.transforms)
            pred3 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred3.shape, pred_whole.shape)

            # `block_size` and `overlap` are both tuples
            save_dir = osp.join(td, 'pred4')
            self.model.slider_predict(self.image_paths, save_dir, (128, 100),
                                      (10, 5), self.transforms)
            pred4 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred4.shape, pred_whole.shape)

            # `block_size` larger than image size
            save_dir = osp.join(td, 'pred5')
            self.model.slider_predict(self.image_paths, save_dir, 512, 0,
                                      self.transforms)
            pred5 = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred5.shape, pred_whole.shape)

    def test_merge_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            # Whole-image inference using predict()
            pred_whole = self.model.predict(self.image_paths, self.transforms)
            pred_whole = pred_whole['label_map']

            # 'keep_first'
            save_dir = osp.join(td, 'keep_first')
            self.model.slider_predict(
                self.image_paths,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='keep_first')
            pred_keepfirst = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_keepfirst.shape, pred_whole.shape)

            # 'keep_last'
            save_dir = osp.join(td, 'keep_last')
            self.model.slider_predict(
                self.image_paths,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='keep_last')
            pred_keeplast = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_keeplast.shape, pred_whole.shape)

            # 'vote'
            save_dir = osp.join(td, 'vote')
            self.model.slider_predict(
                self.image_paths,
                save_dir,
                128,
                64,
                self.transforms,
                merge_strategy='vote')
            pred_vote = T.decode_image(
                osp.join(save_dir, self.basename),
                to_uint8=False,
                decode_sar=False)
            self.check_output_equal(pred_vote.shape, pred_whole.shape)

    def test_geo_info(self):
        with tempfile.TemporaryDirectory() as td:
            _, geo_info_in = T.decode_image(
                self.image_paths[0], read_geo_info=True)
            self.model.slider_predict(self.image_paths, td, 128, 0,
                                      self.transforms)
            _, geo_info_out = T.decode_image(
                osp.join(td, self.basename), read_geo_info=True)
            self.assertEqual(geo_info_out['geo_trans'],
                             geo_info_in['geo_trans'])
            self.assertEqual(geo_info_out['geo_proj'], geo_info_in['geo_proj'])
