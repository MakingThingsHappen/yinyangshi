# -*- coding: utf-8 -*-

import cv2
import errors
import numpy as np


class ImageLocation(object):
    def __init__(self):
        self.src_img_rgb = None  # 原图像对象
        self.tgt_img_rgb = None  # 目标图像对象
        self.pt = None  # 匹配到的对象

    @staticmethod
    def _help(x):
        if x < 0:
            return 0
        if x > 255:
            return 255
        return x

    def get_color_mean(self, img, color=(), mask=0):
        """得到颜色占比

        Args:
            img(str or object):
            color(tuple): [R, G, B] -> (0, 0, 0)
            mask(int): 偏移范围

        Returns(float):

        """
        if isinstance(img, (str, unicode)):
            img = cv2.imread(img)

        lower, upper = ([self._help(color[2] - mask), self._help(color[1] - mask), self._help(color[0] - mask)],
                        [self._help(color[2] + mask), self._help(color[1] + mask), self._help(color[0] + mask)])
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(img, lower, upper)
        return cv2.countNonZero(mask) / float(img.size / 3)

    @staticmethod
    def draw_rect(pt, w, h, src_rgb, out="rect.png"):
        """在匹配到的区域以dx, dy为偏移量画矩形.

        """
        cv2.rectangle(src_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        cv2.imwrite(out, src_rgb)
        return True

    @staticmethod
    def _get_location_obj(src_img_rgb, tgt_img_rgb, threshold=0.8, mode=cv2.TM_CCOEFF_NORMED):
        img_gray = cv2.cvtColor(src_img_rgb, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, tgt_img_rgb, mode)
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            return pt
        return None

    def get_location_obj(self, source, target, threshold=0.8):
        """从source中获取target的坐标

        :param source:
        :param target:
        :return:
        """
        self.src_img_rgb = cv2.imread(source)
        self.tgt_img_rgb = cv2.imread(target, 0)
        return self._get_location_obj(self.src_img_rgb, self.tgt_img_rgb, threshold=threshold)

    @classmethod
    def get_match_image_loc(cls, src, target, ratio=0.55):
        if isinstance(src, (str, unicode)):
            src = cv2.imread(src, 0)
        if isinstance(target, (str, unicode)):
            target = cv2.imread(target, 0)

        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(target, None)
        kp2, des2 = sift.detectAndCompute(src, None)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test
        good = []
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good.append([m])
        if not good:
            return [], (None, None)
        pt = cls.get_loc(good[0][0], kp2)
        return good, pt

    @staticmethod
    def get_loc(mat, kp2):
        img2_idx = mat.trainIdx
        x, y = kp2[img2_idx].pt
        return int(x), int(y)

    def get_target_shape(self):
        w, h = self.tgt_img_rgb.shape[::-1]
        return int(w), int(h)

    def get_location(self, source, target, threshold=0.8):
        """从source中获取target的中心坐标

        Args:
            source(str):
            target(str):
            threshold:

        Returns:

        """
        try:
            pt = self.get_location_obj(source, target, threshold)
            if pt:
                return int(pt[0]), int(pt[1])
            _, pt = self.get_match_image_loc(source, target)
            return int(pt[0]), int(pt[1])

        except Exception:
            raise errors.LocationDoesNotFound


if __name__ == '__main__':
    source = "images/capture.jpg"
    target = "images/yys.png"
    w, h = ImageLocation.get_location(source, target)
    print(w, h)
