"""Phase manager for classification: handles production/evaluation switching."""
from __future__ import annotations


class ClassificationPhaseManager:
    PHASE_PRODUCTION = "production"
    PHASE_EVALUATION = "evaluation"

    def __init__(
        self,
        *,
        evaluation_phase: bool,
        prod_threshold: int,
        eval_threshold: int,
    ) -> None:
        if prod_threshold < 1:
            raise ValueError(f"prod_threshold must be >= 1, got {prod_threshold}")
        if eval_threshold < 1:
            raise ValueError(f"eval_threshold must be >= 1, got {eval_threshold}")

        self.current_phase = self.PHASE_EVALUATION if evaluation_phase else self.PHASE_PRODUCTION

        # Contatori “per fase” (come nel diagramma UML)
        self.prod_counter = 0
        self.eval_counter = 0

        self.prod_threshold = prod_threshold
        self.eval_threshold = eval_threshold

    @property
    def evaluation_phase(self) -> bool:
        return self.current_phase == self.PHASE_EVALUATION

    def increment_counter(self) -> None:
        if self.current_phase == self.PHASE_EVALUATION:
            self.eval_counter += 1
        else:
            self.prod_counter += 1

    def check_thresholds(self) -> bool:
        """Return True if a phase switch happened."""
        if self.current_phase == self.PHASE_EVALUATION and self.eval_counter >= self.eval_threshold:
            self.switch_phase()
            return True

        if self.current_phase == self.PHASE_PRODUCTION and self.prod_counter >= self.prod_threshold:
            self.switch_phase()
            return True

        return False

    def switch_phase(self) -> None:
        if self.current_phase == self.PHASE_EVALUATION:
            self.eval_counter = 0
            self.current_phase = self.PHASE_PRODUCTION
        else:
            self.prod_counter = 0
            self.current_phase = self.PHASE_EVALUATION

    def on_session_completed(self) -> bool:
        """Call once after each classified session."""
        self.increment_counter()
        return self.check_thresholds()
