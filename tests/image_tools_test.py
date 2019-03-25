# -*- coding: utf-8 -*-
import os
import cv2
from unittest import TestCase
from image_tools import ImageLocation

test_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.join(test_dir, 'images')
rc_dir = os.path.join(os.path.dirname(test_dir), 'rc')

SRC = os.path.join(base_dir, "startup.jpg")

YYS = os.path.join(base_dir, "emulator.jpg")
YYS_T = os.path.join(rc_dir, "yys.png")

WAIT2 = os.path.join(base_dir, "wait2.jpg")
WAIT2_T = os.path.join(rc_dir, "wait2.png")

WAIT5 = os.path.join(base_dir, "wait5.jpg")
WAIT5_T = os.path.join(rc_dir, "wait5.png")

JOIN2 = os.path.join(base_dir, "join2.jpg")
JOIN2_T = os.path.join(rc_dir, "join2.png")

MEAN = os.path.join(base_dir, "mean.jpg")

TARGET = os.path.join(base_dir, "wait.png")
OUT = os.path.join(base_dir, "out.png")


class ImageToolTest(TestCase):
    def test_get_location_obj(self):
        il = ImageLocation()
        x = il.get_location_obj(SRC, TARGET)
        self.assertIsNotNone(x)

    def test_draw_rect(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(SRC)
        tgt_img_rgb = cv2.imread(TARGET, 0)
        pt = il._get_location_obj(src_img_rgb, tgt_img_rgb)
        w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_draw_rect_wait2(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(WAIT2)
        tgt_img_rgb = cv2.imread(WAIT2_T, 0)
        pt = il._get_location_obj(src_img_rgb, tgt_img_rgb, 0.5)
        w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_draw_rect_wait5(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(WAIT5)
        tgt_img_rgb = cv2.imread(WAIT5_T, 0)
        pt = il.get_location(WAIT5, WAIT5_T, 0.5)
        w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_get_match_image_loc(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(JOIN2, 1)
        tgt_img_rgb = cv2.imread(JOIN2_T, 1)
        _, pt = il.get_match_image_loc(JOIN2, JOIN2_T)
        _, w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_get_location(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(JOIN2, 1)
        tgt_img_rgb = cv2.imread(JOIN2_T, 1)
        pt = il.get_location(JOIN2, JOIN2_T)
        _, w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_draw_rect_yys(self):
        il = ImageLocation()
        src_img_rgb = cv2.imread(YYS)
        tgt_img_rgb = cv2.imread(YYS_T, 0)

        pt = il._get_location_obj(src_img_rgb, tgt_img_rgb, 0.8)
        w, h = tgt_img_rgb.shape[::-1]
        draw = il.draw_rect(pt, w, h, src_img_rgb, OUT)
        self.assertEqual(draw, True)

    def test_get_color_mean(self):
        il = ImageLocation()
        img = cv2.imread(MEAN)
        ratio = il.get_color_mean(img, (0, 0, 0))
        self.assertEqual(ratio > 0.8, True)

    def test_get_color_mean_with_str(self):
        il = ImageLocation()
        ratio = il.get_color_mean(MEAN, (0, 0, 0))
        self.assertEqual(ratio > 0.8, True)
