class CoverageReportModel:
    def generate_coverage_report(self, sessions: list, min_len: int, max_len: int) -> dict:
        issues = []
        
        # Verifica copertura (esempio: lunghezza tweet nel range corretto)
        for s in sessions:
            if not (min_len <= s.tweet_length <= max_len):
                issues.append(f"Session {s.uuid}: Length {s.tweet_length} out of range [{min_len}-{max_len}]")
            
            # Qui si potrebbero aggiungere controlli sull'audio_db se richiesto dal PDF
        
        coverage_satisfied = (len(issues) == 0)
        
        return {
            "coverage_satisfied": coverage_satisfied,
            "issues_count": len(issues),
            "sample_issues": issues[:5]
        }