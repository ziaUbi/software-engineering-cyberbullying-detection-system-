import random

class LearningSetSplitter:
    def generate_learning_sets(self, sessions: list, train_pct: float, val_pct: float) -> dict:
        # Mescola le sessioni per casualità
        random.shuffle(sessions)
        
        total = len(sessions)
        n_train = int(total * train_pct)
        n_val = int(total * val_pct)
        
        training = sessions[:n_train]
        validation = sessions[n_train : n_train + n_val]
        test = sessions[n_train + n_val :]
        
        # Converte in dizionari per l'invio JSON
        return {
            "training_set": [s.to_dict() for s in training],
            "validation_set": [s.to_dict() for s in validation],
            "test_set": [s.to_dict() for s in test]
        }