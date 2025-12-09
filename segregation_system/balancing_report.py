class BalancingReportModel:
    def generate_balancing_report(self, sessions: list, tolerance: float) -> dict:
        total = len(sessions)
        if total == 0:
            return {"is_balanced": False, "msg": "No sessions"}

        # Conta le classi (es. "Cyberbullying" vs "Safe")
        counts = {}
        for s in sessions:
            label = s.label
            counts[label] = counts.get(label, 0) + 1

        is_balanced = True
        report_details = {}
        
        # Logica: in un sistema binario ideale 50/50. 
        # Tolleranza applicata rispetto alla distribuzione equa.
        ideal_ratio = 1.0 / len(counts) if len(counts) > 0 else 0
        
        for label, count in counts.items():
            ratio = count / total
            diff = abs(ratio - ideal_ratio)
            
            if diff > tolerance:
                is_balanced = False
            
            report_details[label] = {
                "count": count,
                "percentage": round(ratio * 100, 2)
            }

        return {
            "total_sessions": total,
            "details": report_details,
            "is_balanced": is_balanced
        }