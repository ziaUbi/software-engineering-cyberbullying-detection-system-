import os
import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from segregation_system.coverage_report.coverage_report import CoverageReportData


class CoverageReportView:
    """
    Prende un CoverageReportData e disegna un radar / bubble chart
    con 4 assi:
    - Tweet lenght [5,40]
    - Game Events
    - Bad Words
    - dB Gain [40,120]
    """
    @staticmethod
    def safe_max(values, default=0):
        return max(values) if values else default

    def normalize(self, values):
        if not values:
            return []
        max_v = max(values)
        if max_v == 0:
            return [0 for _ in values]
        return [v / max_v for v in values]

    @staticmethod
    def show_coverage_report(report: CoverageReportData, workspace_dir, title: Optional[str] = "Coverage Report"):
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        angle_tweet = math.radians(135)   
        angle_events = math.radians(45)  
        angle_badwords = math.radians(315)  
        angle_db = math.radians(225)      

        r_max = 1.0
        ax.set_rlim(0, r_max)

        ax.set_rgrids(
            np.linspace(0.2, r_max, 4),
            angle=0,
            fontsize=8,
            linestyle="dotted",
        )

        ax.set_xticklabels([])

        # ---------------- Tweet length ----------------
        tl_map = report.tweet_length_map or {}
        if tl_map:
            lengths = sorted(tl_map.keys())
            min_len = min(lengths)
            max_len = max(lengths)
        else:
            # default range come da titolo
            min_len, max_len = 5, 40
            lengths = []
        
        max_count_tl = safe_max(tl_map.values(), default=1)

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

        # ---------------- Game events ----------------
        events_map = report.events_map or {}
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

        # ---------------- Bad words ----------------
        bw_map = report.bad_words_map or {}
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


        # ---------------- dB Gain ----------------
        db_map = report.audio_db_map or {}
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
        # plt.show()
        plt_path = "segregation_system/" + workspace_dir + '/coverage_report.png'
        plt.savefig(plt_path)
        return