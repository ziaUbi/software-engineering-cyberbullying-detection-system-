from coverage_report.coverage_report import CoverageReportData

class CoverageReportModel:
    def generate_coverage_report(self, sessions: list) -> dict:

        bow_vocabulary = ["fuck", "bulli", "muslim", "gay", "nigger", "rape"]
        coverage_satisfied = True

        report = CoverageReportData(
            total_sessions=len(sessions),
            tweet_length_list=[len(s.tweet) for s in sessions],
            audio_db_list=[s.audio_db_level for s in sessions],
            badWords=[sum(1 for word in bow_vocabulary if word in s.tweet.lower()) for s in sessions],
            events_list=[len(s.events) for s in sessions],
            coverage_satisfied=coverage_satisfied
        )

        return report
