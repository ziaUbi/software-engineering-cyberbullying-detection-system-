import os
import math
import numpy as np
from typing import Optional
import matplotlib.pyplot as plt

from segregation_system.coverage_report.coverage_report import CoverageReportData

class CoverageReportView:
    @staticmethod
    def show_coverage_report(report: CoverageReportData, workspace_dir, title: Optional[str] = "Coverage Report"):
        fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, polar=True)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        angle_tweet = math.radians(135)   
        angle_events = math.radians(45)  
        angle_badwords = math.radians(315)  
        angle_db = math.radians(225)      

        r_max = 1.0
        ax.set_rlim(0, r_max)

        # Draw concentric circles
        ax.set_rgrids(np.linspace(0.2, r_max, 5), angle=0, fontsize=8, color='gray', alpha=0.5)
        ax.set_xticklabels([])

        # ---------------- Tweet length ----------------
        tl_map = report.tweet_length_map or {}
        if not tl_map:
            return
        lengths = sorted(tl_map.keys())
        min_len = min(lengths)
        max_len = max(lengths)
        if min_len == max_len:
            max_len += 1
        
        max_count = max(tl_map.values()) if tl_map else 1

        for length, count in tl_map.items():
            if count < 3:
                continue
            normalized_r = 0.2 + 0.8 * (length - min_len) / (max_len - min_len)     # Normalize position along axis [5,40] -> [0.2, 1.0]
            bubble_size = 100 + (count / max_count) * 1500      # Bubble size proportional to count
            ax.scatter(angle_tweet, normalized_r, s=bubble_size, alpha=0.6, color='lightblue', edgecolors='black', linewidth=1.5)

        ax.text(angle_tweet, r_max + 0.15, f'Tweet length\n[{min_len},{max_len}]', ha='center', va='center', fontsize=12, fontweight='bold')

        # ---------------- Game events ----------------
        events_map = report.events_map or {}
        if events_map:
            event_names = ["Score", "Sending-off", "Caution", "Substitution", "Foul"]
            max_event_count = max(events_map.values()) if events_map else 1
            
            for i, event_name in enumerate(event_names):
                count = events_map.get(event_name, 0)
                normalized_r = 0.3 + (i / (len(event_names) - 1)) * 0.6
                bubble_size = 100 + (count / max_event_count) * 1500
                ax.scatter(angle_events, normalized_r, s=bubble_size, alpha=0.6, color='lightgreen', edgecolors='black', linewidth=1.5)
                ax.text(angle_events + 0.1, normalized_r, event_name, ha='left', va='center', fontsize=9)

        ax.text(angle_events, r_max + 0.15, 'Game Events', ha='center', va='center', fontsize=12, fontweight='bold')

        # ---------------- Bad words ----------------
        bw_map = report.bad_words_map or {}
        if bw_map:
            word_names = ["Fuck", "Bulli", "Muslim", "Gay", "Nigger", "Rape"]
            max_bw_count = max(bw_map.values()) if bw_map else 1
            
            for i, word in enumerate(word_names):
                count = bw_map.get(word.lower(), 0)
                normalized_r = 0.3 + (i / (len(word_names) - 1)) * 0.6
                bubble_size = 100 + (count / max_bw_count) * 1500
                ax.scatter(angle_badwords, normalized_r, s=bubble_size, alpha=0.6, color='lightcoral', edgecolors='black', linewidth=1.5)
                display_word = word if word.lower() != "nigger" else "Ni****"
                ax.text(angle_badwords - 0.1, normalized_r, display_word, ha='right', va='center', fontsize=9)

        ax.text(angle_badwords, r_max + 0.15, 'Bad Words', ha='center', va='center', fontsize=12, fontweight='bold')
       
        # ---------------- dB Gain ----------------
        db_map = report.audio_db_map or {}
        if db_map:
            decibels = sorted(db_map.keys())
            min_db = min(decibels)
            max_db = max(decibels)
            if min_db == max_db:
                max_db += 1  
            max_db_count = max(db_map.values()) if db_map else 1
            
            sorted_dbs = sorted(db_map.items())
            for db_value, count in sorted_dbs: 
                if count < 4:
                    continue
                normalized_r = 0.2 + 0.8 * (db_value - min_db) / (max_db - min_db)
                bubble_size = 100 + (count / max_db_count) * 1500
                ax.scatter(angle_db, normalized_r, s=bubble_size, alpha=0.6, color='yellow', edgecolors='black', linewidth=1.5)

        ax.text(angle_db, r_max + 0.15, f'dB Gain\n[{min_db},{max_db}]', ha='center', va='center', fontsize=12, fontweight='bold')

        # ---------------- Center info ----------------
        total = report.total_sessions
        ax.text(0, 0, f'{total}\nSessions', ha='center', va='center', fontsize=14, fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt_path = "segregation_system/" + workspace_dir + '/coverage_report.png'
        plt.savefig(plt_path)
        return