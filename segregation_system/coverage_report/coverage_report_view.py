# coverage_report_view.py

import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from coverage_report.coverage_report import CoverageReportData


class CoverageReportView:
    """
    Prende un CoverageReportData e disegna un radar / bubble chart
    con 4 assi:
    - Tweet lenght [5,40]
    - Game Events
    - Bad Words
    - dB Gain [40,120]
    """

    def __init__(self, report: CoverageReportData):
        self.report = report

    def _normalize(self, values):
        """Normalizza una lista di valori in [0, 1] (gestendo il caso tutti zero)."""
        if not values:
            return []
        max_v = max(values)
        if max_v == 0:
            return [0 for _ in values]
        return [v / max_v for v in values]

    def plot(self, title: Optional[str] = "Coverage Report"):
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        # Imposto il nord verso l’alto e giro in senso orario
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        # Angoli dei 4 assi (in radianti)
        angle_tweet = math.radians(135)   # in alto a sinistra
        angle_events = math.radians(45)   # in alto a destra
        angle_badwords = math.radians(315)  # in basso a destra
        angle_db = math.radians(225)      # in basso a sinistra

        # Raggio massimo (solo estetico)
        r_max = 1.0
        ax.set_rlim(0, r_max)

        # Disegno cerchi concentrici (come nel grafico di esempio)
        ax.set_rgrids(
            np.linspace(0.2, r_max, 4),
            angle=0,
            fontsize=8,
            linestyle="dotted",
        )

        # Nascondo le etichette dell’asse angolare
        ax.set_xticklabels([])

        # ---------------- Tweet length ----------------
        tweet_values = self.report.tweet_length_list
        tweet_norm = self._normalize(tweet_values)
        # uso i valori normalizzati come raggio
        for r in tweet_norm:
            if r <= 0:
                continue
            ax.scatter(angle_tweet, r, s=300 * r ** 2, edgecolors="black", facecolors="white")

        ax.text(
            angle_tweet,
            r_max + 0.05,
            "Tweet lenght\n[5,40]",
            ha="center",
            va="center",
            fontsize=11,
        )

        # ---------------- Game events ----------------
        event_values = self.report.events_list
        event_norm = self._normalize(event_values)
        event_labels = ["Score", "Sending-off", "Caution", "Substitution", "Foul"]

        for r, label in zip(event_norm, event_labels):
            if r <= 0:
                continue
            ax.scatter(angle_events, r, s=300 * r ** 2, edgecolors="black", facecolors="white")
            ax.text(angle_events, r, label, fontsize=8, ha="left", va="center")

        ax.text(
            angle_events,
            r_max + 0.05,
            "Game Events",
            ha="center",
            va="center",
            fontsize=11,
        )

        # ---------------- Bad words ----------------
        bw_values = self.report.badWords
        bw_norm = self._normalize(bw_values)
        bw_labels = ["F**k", "Bulli", "Muslim", "Gay", "Ni***r", "Rape"]

        for r, label in zip(bw_norm, bw_labels):
            if r <= 0:
                continue
            ax.scatter(angle_badwords, r, s=300 * r ** 2, edgecolors="black", facecolors="white")
            ax.text(angle_badwords, r, label, fontsize=8, ha="right", va="center")

        ax.text(
            angle_badwords,
            r_max + 0.05,
            "Bad Words",
            ha="center",
            va="center",
            fontsize=11,
        )

        # ---------------- dB Gain ----------------
        db_values = self.report.audio_db_list
        db_norm = self._normalize(db_values)

        for r in db_norm:
            if r <= 0:
                continue
            ax.scatter(angle_db, r, s=300 * r ** 2, edgecolors="black", facecolors="white")

        ax.text(
            angle_db,
            r_max + 0.05,
            "dB Gain\n[40,120]",
            ha="center",
            va="center",
            fontsize=11,
        )

        # Bordo esterno spesso (come nell'immagine)
        circle = plt.Circle(
            (0.0, 0.0),
            r_max,
            transform=ax.transData._b,
            fill=False,
            linewidth=3,
            color="black",
        )
        ax.add_artist(circle)

        plt.title(title)
        plt.tight_layout()
        plt.show()

# coverage_report_view.py

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from coverage_report.coverage_report import CoverageReportData
import math


class CoverageReportView:
    """
    Riceve un CoverageReportData e disegna il radar/bubble chart
    come nell'immagine di riferimento.
    """

    def __init__(self, report: CoverageReportData):
        self.report = report

    @staticmethod
    def _safe_max(values, default=0):
        return max(values) if values else default

    def plot(self, title: Optional[str] = "Coverage Report"):
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        # Nord verso l'alto e direzione oraria
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        # Angoli dei 4 assi
        angle_tweet = math.radians(135)      # in alto a sinistra
        angle_events = math.radians(45)      # in alto a destra
        angle_badwords = math.radians(315)   # in basso a destra
        angle_db = math.radians(225)         # in basso a sinistra

        r_max = 1.0
        ax.set_rlim(0, r_max)

        # Cerchi concentrici
        ax.set_rgrids(
            np.linspace(0.2, r_max, 4),
            angle=0,
            fontsize=8,
            linestyle="dotted",
        )

        # Nascondo etichette angolari
        ax.set_xticklabels([])

        # ------------------------------------------------------------------
        # 1) Tweet length
        # ------------------------------------------------------------------
        tl_map = self.report.tweet_length_map or {}
        if tl_map:
            lengths = sorted(tl_map.keys())
            min_len = min(lengths)
            max_len = max(lengths)
        else:
            # default range come da titolo
            min_len, max_len = 5, 40
            lengths = []

        max_count_tl = self._safe_max(tl_map.values(), default=1)

        for length in lengths:
            count = tl_map[length]
            # raggio in base alla lunghezza
            if max_len != min_len:
                r = (length - min_len) / (max_len - min_len)
            else:
                r = 0.5
            r = 0.1 + 0.8 * r  # evito di stare troppo al centro/bordo

            # dimensione bolla in base al conteggio
            size = 50 + 400 * (count / max_count_tl)

            ax.scatter(angle_tweet, r, s=size, edgecolors="black", facecolors="white")
            ax.text(
                angle_tweet,
                r,
                str(length),
                fontsize=8,
                ha="center",
                va="center",
            )

        ax.text(
            angle_tweet,
            r_max + 0.05,
            "Tweet lenght\n[5,40]",
            ha="center",
            va="center",
            fontsize=12,
        )

        # ------------------------------------------------------------------
        # 2) Game Events
        # ------------------------------------------------------------------
        events_map = self.report.events_map or {}
        event_names = ["Score", "Sending-off", "Caution", "Substitution", "Foul"]
        max_ev = self._safe_max(events_map.values(), default=1)

        for name in event_names:
            value = events_map.get(name, 0)
            if value <= 0:
                continue
            r = value / max_ev
            r = 0.1 + 0.8 * r

            size = 80 + 300 * (value / max_ev)

            ax.scatter(angle_events, r, s=size, edgecolors="black", facecolors="white")
            ax.text(
                angle_events,
                r,
                name,
                fontsize=8,
                ha="left",
                va="center",
            )

        ax.text(
            angle_events,
            r_max + 0.05,
            "Game Events",
            ha="center",
            va="center",
            fontsize=12,
        )

        # ------------------------------------------------------------------
        # 3) Bad Words
        # ------------------------------------------------------------------
        bw_map = self.report.bad_words_map or {}
        bw_order = ["fuck", "bulli", "muslim", "gay", "nigger", "rape"]
        label_map = {
            "fuck": "F**k",
            "bulli": "Bulli",
            "muslim": "Muslim",
            "gay": "Gay",
            "nigger": "Ni****r",
            "rape": "Rape",
        }

        max_bw = self._safe_max(bw_map.values(), default=1)

        for key in bw_order:
            value = bw_map.get(key, 0)
            if value <= 0:
                continue
            r = value / max_bw
            r = 0.1 + 0.8 * r
            size = 60 + 300 * (value / max_bw)

            ax.scatter(angle_badwords, r, s=size, edgecolors="black", facecolors="white")
            ax.text(
                angle_badwords,
                r,
                label_map.get(key, key),
                fontsize=8,
                ha="right",
                va="center",
            )

        ax.text(
            angle_badwords,
            r_max + 0.05,
            "Bad Words",
            ha="center",
            va="center",
            fontsize=12,
        )

        # ------------------------------------------------------------------
        # 4) dB Gain
        # ------------------------------------------------------------------
        db_map = self.report.audio_db_map or {}
        if db_map:
            db_values = sorted(db_map.keys())
            min_db = min(db_values)
            max_db = max(db_values)
        else:
            min_db, max_db = 40, 120
            db_values = []

        max_count_db = self._safe_max(db_map.values(), default=1)

        for db in db_values:
            count = db_map[db]
            if max_db != min_db:
                r = (db - min_db) / (max_db - min_db)
            else:
                r = 0.5
            r = 0.1 + 0.8 * r

            size = 50 + 400 * (count / max_count_db)
            # valore normalizzato da scrivere dentro la bolla
            norm_count = round(count / max_count_db, 2)

            ax.scatter(angle_db, r, s=size, edgecolors="black", facecolors="white")
            ax.text(
                angle_db,
                r,
                f"{norm_count}",
                fontsize=8,
                ha="center",
                va="center",
            )

        ax.text(
            angle_db,
            r_max + 0.05,
            "dB Gain\n[40,120]",
            ha="center",
            va="center",
            fontsize=12,
        )

        # Bordo esterno spesso
        circle = plt.Circle(
            (0.0, 0.0),
            r_max,
            transform=ax.transData._b,
            fill=False,
            linewidth=3,
            color="black",
        )
        ax.add_artist(circle)

        plt.title(title)
        plt.tight_layout()
        plt.show()
