import time
from segregation_parameters import SegregationSystemConfiguration
from database.database_manager import PreparedSessionDatabaseController
from logic.balancing_report import BalancingReportModel
from logic.coverage_report import CoverageReportModel
from logic.learning_set_splitter import LearningSetSplitter
from communication.segregation_communication import SegregationCommunication
from models.prepared_session import PreparedSession

class SegregationSystemOrchestrator:
    def __init__(self, base_dir="."):
        # 1. Carica parametri
        SegregationSystemConfiguration.load_parameters(base_dir)
        
        # 2. Inizializza componenti
        self.db = PreparedSessionDatabaseController(f"{base_dir}/database/segregation.db")
        self.comm = SegregationCommunication()
        
        # 3. Logica
        self.balancing_logic = BalancingReportModel()
        self.coverage_logic = CoverageReportModel()
        self.splitter = LearningSetSplitter()
        
        self.running = True

    def start(self):
        print("--- Segregation System Orchestrator Started ---")
        self.comm.start_listening()

        while self.running:
            # A. Controllo nuovi messaggi (Sessioni)
            session_data = self.comm.get_session()
            if session_data:
                # Converti dict in oggetto e salva su DB
                session = PreparedSession.from_dict(session_data)
                self.db.store_prepared_session(session)
            
            # B. Controllo Configurazione (opzionale per runtime update)
            config_data = self.comm.get_config()
            if config_data:
                print(f"[Orchestrator] Configuration received: {config_data}")
                # Aggiorna LOCAL_PARAMETERS se necessario

            # C. Logica principale (Check threshold)
            self._process_data()
            
            time.sleep(1)

    def _process_data(self):
        # Parametri
        params = SegregationSystemConfiguration.LOCAL_PARAMETERS
        min_sessions = params["min_sessions_for_processing"]
        current_count = self.db.get_number_of_sessions_stored()

        # Se non abbiamo abbastanza sessioni, attendiamo
        if current_count < min_sessions:
            return

        print(f"\n[Process] Threshold reached ({current_count}). Starting analysis...")
        all_sessions = self.db.get_all_prepared_sessions()

        # 1. Generazione Balancing Report
        print("--- Balancing Report ---")
        bal_report = self.balancing_logic.generate_balancing_report(
            all_sessions, 
            params["balancing_report_threshold"]
        )
        print(f"Result: {bal_report}")
        
        # Simulazione decisione Data Analyst (nel software reale sarebbe una GUI o attesa messaggio)
        # Qui assumiamo approvazione automatica se bilanciato, o log di errore
        if not bal_report["is_balanced"]:
            print("[Process] Data NOT balanced. Waiting for more data...")
            return 

        # 2. Generazione Coverage Report
        print("--- Coverage Report ---")
        cov_report = self.coverage_logic.generate_coverage_report(
            all_sessions, 
            params["min_tweet_length"], 
            params["max_tweet_length"]
        )
        print(f"Issues found: {cov_report['issues_count']}")
        
        if not cov_report["coverage_satisfied"]:
            print("[Process] Coverage NOT satisfied. Review data.")
            # In un caso reale, qui si scarterebbero sessioni o si invierebbe alert
            return

        # 3. Generazione Learning Sets
        print("--- Generating Learning Sets ---")
        learning_sets = self.splitter.generate_learning_sets(
            all_sessions,
            params["training_set_percentage"],
            params["validation_set_percentage"]
        )
        
        # 4. Invio al Development System
        success = self.comm.send_learning_sets(learning_sets)
        
        if success:
            print("[Process] Sets sent. Clearing database...")
            self.db.remove_all_prepared_sessions()
        else:
            print("[Process] Failed to send sets. Retrying later.")