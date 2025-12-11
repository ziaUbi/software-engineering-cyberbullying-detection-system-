from typing import List, Any
from collections import Counter, defaultdict

from segregation_system.coverage_report.coverage_report import CoverageReportData
from segregation_system.prepared_session import PreparedSession

class CoverageReportModel:
    def generate_coverage_report(self, sessions: List[PreparedSession]) -> dict:

        bow_vocabulary = ["fuck", "bulli", "muslim", "gay", "nigger", "rape"]
        
        # --------- Tweet length: {lenght -> count} ---------
        tweet_length_counter: Counter[int] = Counter()
        for s in sessions:
            length = getattr(s, "tweet_length", None)
            if length is not None:
                tweet_length_counter[int(length)] += 1


        # --------- Bad words: {word -> occurrences} ---------
        bad_words_map = {}
        for word in bow_vocabulary:
            attr_name = f"word_{word}"
            total_for_word = 0
            for s in sessions:
                total_for_word += int(getattr(s, attr_name, 0))
            bad_words_map[word] = total_for_word


        # --------- Audio dB: {decibel value -> count} ---------
        audio_db_counter: Counter[int] = Counter()
        for s in sessions:
            for band_idx in range(20):
                attr_name = f"audio_{band_idx}"
                value = getattr(s, attr_name, None)
                if value is None:
                    continue
                db_value = int(round(float(value)))
                audio_db_counter[db_value] += 1

        # --------- Events: {event -> count} ---------
        total_score = 0
        total_sending_off = 0
        total_caution = 0
        total_substitution = 0
        total_foul = 0
        total_unknown = 0

        for s in sessions:
            total_score += int(getattr(s, "event_score", 0))
            total_sending_off += int(getattr(s, "event_sending_off", 0))
            total_caution += int(getattr(s, "event_caution", 0))
            total_substitution += int(getattr(s, "event_substitution", 0))
            total_foul += int(getattr(s, "event_foul", 0))
            total_unknown += int(getattr(s, "event_unknown", 0))

        events_map = {
            "Score": total_score,
            "Sending-off": total_sending_off,
            "Caution": total_caution,
            "Substitution": total_substitution,
            "Foul": total_foul,
            "Unknown": total_unknown
        }

        # --------- Sessions ---------
        total_sessions = len(sessions)

        report = CoverageReportData(
            total_sessions=total_sessions,
            tweet_length_map=dict(tweet_length_counter),
            audio_db_map=dict(audio_db_counter),
            bad_words_map=bad_words_map,
            events_map=events_map,
        )

        return report


        
        

        return report
