# Cyberbullying Detection System
## 📌 Overview
This project is a comprehensive software engineering solution designed to detect cyberbullying in social media interactions (specifically **tweets**). It implements a complete Machine Learning pipeline, structured into distinct modular systems that handle everything from data ingestion to production deployment and evaluation.

The system is built using Python and follows a rigorous architectural pattern, separating concerns into specific subsystems (Ingestion, Preparation, Segregation, Development, Production, and Evaluation).

## 🛠 Architecture
The application is divided into several autonomous subsystems, orchestrated to form a pipeline:

- **Ingestion System:** Responsible for receiving raw data and storing it into the raw database.

- **Preparation System:** Validates, cleans, and transforms raw data into a structured format suitable for processing.

- **Segregation System:** Manages dataset splitting (Training, Validation, Testing) and ensures data balancing.

- **Development System:** Handles the model training, validation, and testing phases. It generates performance reports and saves the trained models.

- **Production System:** Deploys the trained model to classify new incoming data in a production environment.

- **Evaluation System:** Monitors and evaluates the performance of the system over time.

- **Service Class:**  Simulates the external environment (client), sending raw data (tweets) and receiving classification results.

## 📑 Features
- *Modular Architecture:* High separation of concerns makes the code maintainable and scalable.

- *Data Validation:* rigorous JSON schema validation for inputs and configuration files.

- *Automated Pipeline:* Orchestrators manage the flow of data between subsystems.

- *Model Persistence:* Saves trained classifiers (.sav files) for reuse.

- *Reporting:* Generates reports for balancing, coverage, and training performance (including plots).

- *Logging:* Comprehensive logging for both development and production phases.
