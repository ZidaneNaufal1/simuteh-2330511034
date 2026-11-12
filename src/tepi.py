"""Operator dan ambang deteksi tepi untuk SIMUTEH P5."""

import cv2
import numpy as np

SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
PREWITT_X = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], np.float32)


def gradien(g):
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    return np.hypot(gx, gy)


def tepi_sobel(g, T=100):
    return (gradien(g) > T).astype(np.uint8) * 255


def tepi_prewitt(g, T=75):
    g = g.astype(np.float32)
    gx = cv2.filter2D(g, cv2.CV_32F, PREWITT_X)
    gy = cv2.filter2D(g, cv2.CV_32F, PREWITT_X.T)
    return (np.hypot(gx, gy) > T).astype(np.uint8) * 255


def tepi_log(g, sigma=3.0, frac=0.2):
    lap = cv2.Laplacian(cv2.GaussianBlur(g.astype(np.float32), (0, 0), sigma), cv2.CV_32F)
    se = np.ones((3, 3), np.uint8)
    mn, mx = cv2.erode(lap, se), cv2.dilate(lap, se)
    silang = (mn < 0) & (mx > 0) & (mx - mn > frac * np.abs(lap).max())
    return silang.astype(np.uint8) * 255


def tepi_canny(g, lo=30, hi=90, sigma=2.0):
    halus = cv2.GaussianBlur(g, (0, 0), sigma) if sigma else g
    return cv2.Canny(halus, lo, hi)


def canny_otomatis(g, s=0.33):
    median = np.median(g)
    return cv2.Canny(g, int(max(0, (1 - s) * median)), int(min(255, (1 + s) * median)))


def canny_persentil(g, q, rasio=0.4, sigma=2.0):
    halus = cv2.GaussianBlur(g, (0, 0), sigma) if sigma else g
    tinggi = float(np.percentile(gradien(halus), q))
    return cv2.Canny(halus, rasio * tinggi, tinggi, L2gradient=True)
