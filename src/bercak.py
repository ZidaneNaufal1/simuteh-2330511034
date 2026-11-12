"""Analisis bercak pada citra BGR yang telah dipraproses."""

import json

import cv2
import numpy as np

from utils_tepi import bercak_awal, mask_daun_awal

PARAM_BERCAK = {
    "kanal": 2, "k": 4.0, "se_bentuk": "elips", "se_open": 5, "se_close": 5,
    "luas_min": 20, "bulat_min": 0.5, "rasio_maks": 1.8,
    "batas_ringan": 0.1, "batas_berat": 2.0, "mm_per_px": 0.4375,
}
BENTUK = {"elips": cv2.MORPH_ELLIPSE, "persegi": cv2.MORPH_RECT, "silang": cv2.MORPH_CROSS}


def elemen(bentuk, ukuran):
    return cv2.getStructuringElement(BENTUK[bentuk], (ukuran, ukuran))


def bersihkan(biner, p):
    """Buang detail tipis dengan opening, lalu tutup celah dengan closing."""
    hasil = biner
    for nama, operasi in [("se_open", cv2.MORPH_OPEN), ("se_close", cv2.MORPH_CLOSE)]:
        ukuran = p[nama]
        if ukuran > 0:
            hasil = cv2.morphologyEx(hasil, operasi, elemen(p["se_bentuk"], ukuran))
    return hasil


def ukur_komponen(biner, mm_per_px=0.4375, konektivitas=8):
    """Ukur area piksel dan geometri kontur tiap komponen foreground."""
    jumlah, label, stat, pusat = cv2.connectedComponentsWithStats(
        (biner > 0).astype(np.uint8), connectivity=konektivitas
    )
    daftar = []
    for i in range(1, jumlah):
        x, y, w, h, luas = map(int, stat[i])
        potongan = (label[y:y + h, x:x + w] == i).astype(np.uint8)
        kontur, _ = cv2.findContours(potongan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        kontur = max(kontur, key=cv2.contourArea)
        keliling = cv2.arcLength(kontur, True)
        sisi_a, sisi_b = cv2.minAreaRect(kontur)[1]
        daftar.append({
            "label": i, "luas_px": luas, "luas_mm2": luas * mm_per_px ** 2,
            "keliling_px": keliling,
            "kebulatan": 4 * np.pi * luas / keliling ** 2 if keliling else 0.0,
            "rasio_aspek": max(1.0, max(sisi_a, sisi_b) / max(1.0, min(sisi_a, sisi_b))),
            "cx": int(pusat[i, 0]), "cy": int(pusat[i, 1]),
        })
    return label, daftar


def lolos_ambang(ukuran, p):
    return (ukuran["luas_px"] >= p["luas_min"]
            and ukuran["kebulatan"] >= p["bulat_min"]
            and ukuran["rasio_aspek"] <= p["rasio_maks"])


def ukur_dan_saring(biner, p):
    label, semua = ukur_komponen(biner, p["mm_per_px"])
    lolos = [ukuran for ukuran in semua if lolos_ambang(ukuran, p)]
    masker = np.isin(label, [ukuran["label"] for ukuran in lolos])
    return masker.astype(np.uint8) * 255, lolos


def analisis_daun(img_praproses, p=None):
    """Kembalikan mask daun, mask bercak, ukuran, persentase, dan kelas."""
    p = {**PARAM_BERCAK, **(p or {})}
    daun = mask_daun_awal(img_praproses)
    luas_daun = np.count_nonzero(daun)
    awal = (bercak_awal(img_praproses, daun, p["kanal"], p["k"])
            if luas_daun else np.zeros_like(daun))
    bersih = cv2.bitwise_and(bersihkan(awal, p), daun)
    bercak, daftar = ukur_dan_saring(bersih, p)
    persen = 100 * np.count_nonzero(bercak) / max(luas_daun, 1)
    kelas = "Sehat"
    if persen >= p["batas_berat"]:
        kelas = "Bercak Berat"
    elif persen >= p["batas_ringan"]:
        kelas = "Bercak Ringan"
    return {"mask_daun": daun, "mask_bercak": bercak, "jumlah_bercak": len(daftar),
            "persen_bercak": round(persen, 3), "kelas": kelas, "bercak": daftar}


def simpan_param(p, path="../hasil/param_bercak.json"):
    with open(path, "w", encoding="utf-8") as file:
        json.dump({**PARAM_BERCAK, **p}, file, indent=2)
