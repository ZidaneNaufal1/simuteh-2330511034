"""Rangkaian praproses SIMUTEH. Masukan dan keluaran adalah citra BGR uint8."""
import json
import cv2
import numpy as np

PARAM_BAWAAN = {'lebar': 640, 'gamma': 1.0, 'clahe_clip': 2.0,
                'clahe_tile': 8, 'penapis': 'median', 'kernel': 3,
                'sigma': 1.0, 'tajam_k': 0.0}

def praproses(img_bgr, p=None):
    p = {**PARAM_BAWAAN, **(p or {})}
    if img_bgr is None or img_bgr.ndim != 3 or img_bgr.shape[2] != 3:
        raise ValueError('Masukan harus berupa citra BGR tiga kanal')
    if p['lebar'] <= 0 or p['gamma'] <= 0 or p['kernel'] < 1 or p['kernel'] % 2 == 0:
        raise ValueError('Lebar dan gamma harus positif, kernel harus ganjil positif')
    tinggi = max(1, round(img_bgr.shape[0] * p['lebar'] / img_bgr.shape[1]))
    img = cv2.resize(img_bgr, (p['lebar'], tinggi), interpolation=cv2.INTER_AREA)
    if p['gamma'] != 1:
        lut = np.array([255 * (i / 255) ** p['gamma'] for i in range(256)]).clip(0, 255).astype(np.uint8)
        img = cv2.LUT(img, lut)
    if p['clahe_clip'] > 0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.createCLAHE(clipLimit=p['clahe_clip'], tileGridSize=(p['clahe_tile'], p['clahe_tile'])).apply(hsv[:, :, 2])
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    k = p['kernel']
    if p['penapis'] == 'rerata':
        img = cv2.blur(img, (k, k))
    elif p['penapis'] == 'gaussian':
        img = cv2.GaussianBlur(img, (k, k), p['sigma'])
    elif p['penapis'] == 'median':
        img = cv2.medianBlur(img, k)
    elif p['penapis'] != 'none':
        raise ValueError('Penapis tidak dikenal')
    if p['tajam_k'] > 0:
        blur = cv2.GaussianBlur(img, (5, 5), p['sigma'])
        img = cv2.addWeighted(img, 1 + p['tajam_k'], blur, -p['tajam_k'], 0)
    return img

def simpan_param(p, path='../hasil/param_praproses.json'):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({**PARAM_BAWAAN, **p}, f, indent=2)
