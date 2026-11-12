"""Muat data dan parameter yang dipakai bersama oleh kedua notebook."""

import json
from pathlib import Path

import cv2
import pandas as pd

from praproses import praproses

AKAR = Path(__file__).resolve().parents[1]
DATA = AKAR / "data" / "sintetis"
HASIL = AKAR / "hasil"


def muat_dataset():
    param = json.loads((HASIL / "param_praproses.json").read_text(encoding="utf-8"))
    label = pd.read_csv(DATA / "label.csv")
    for d in label.itertuples(index=False):
        citra = cv2.imread(str(DATA / "citra" / d.nama_file))
        daun = cv2.imread(str(DATA / "mask_daun" / d.nama_file), cv2.IMREAD_GRAYSCALE)
        bercak = cv2.imread(str(DATA / "mask_bercak" / d.nama_file), cv2.IMREAD_GRAYSCALE)
        if citra is None or daun is None or bercak is None:
            raise FileNotFoundError(d.nama_file)
        pra = praproses(citra, param)
        if not (citra.shape[:2] == pra.shape[:2] == daun.shape == bercak.shape):
            raise ValueError(f"Dimensi citra dan mask berbeda pada {d.nama_file}")
        yield d, citra, pra, daun, bercak


def kanal_gray_r(img):
    return [("Gray", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)), ("R", img[:, :, 2])]
