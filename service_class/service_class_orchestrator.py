import time
import os

from service_class.service_class_parameters import ServiceClassParameters
from service_class.service_receiver import ServiceReceiver
from service_class.record_sender import RecordSender
from service_class.logger import Logger

class ServiceClassOrchestrator:
    """
    Service Class Orchestrator module responsible for managing the Service Class.
    """


    def __init__(self):
        """
        Initialize the Service Class Orchestrator.

        :param basedir: The base directory for the Service Class Orchestrator.
        """

        basedir = os.path.dirname(os.path.abspath(__file__))
        ServiceClassParameters.loadParameters(basedir) # Load the parameters of the Service Class
        self.logger = Logger(basedir, ServiceClassParameters.LOCAL_PARAMETERS["phase"])
        self.serviceReceiver = ServiceReceiver(basedir=basedir, logger=self.logger)
        self.recordSender = RecordSender(basedir=basedir)


    def start(self):
        """
        Start the Service Class Orchestrator.
        """
        print("Service Class started.")

        # Start the Service Receiver server
        self.serviceReceiver.start_receiver()

        if ServiceClassParameters.LOCAL_PARAMETERS["phase"] == "all_phases":
            print("All phases will be tested.")
            print("For each phase, the following sessions will be sent:")
            print(" Development: " + str(ServiceClassParameters.LOCAL_PARAMETERS["development_sessions"]))
            print(" Production: " + str(ServiceClassParameters.LOCAL_PARAMETERS["production_sessions"]))
            print(" Evaluation: " + str(ServiceClassParameters.LOCAL_PARAMETERS["evaluation_sessions"]))

            # Writing headers to the CSV file
            self.logger.write_header("phase,timestamp,status")

            # Dictionary to store the phases and a boolean value to indicate if the labels should be sent
            phases_and_labels = {
                "development": True,
                "production": False,
                "evaluation": True
            }

            for phase, include_labels in phases_and_labels.items():

                if ServiceClassParameters.LOCAL_PARAMETERS[f"{phase}_sessions"] == 0:
                    print(f"Skipping {phase} phase.")
                    continue

                print("Starting " + phase + " phase.")

                # Preparing the bucket for the phase
                bucket = self.recordSender.prepare_bucket(ServiceClassParameters.LOCAL_PARAMETERS[f"{phase}_sessions"], include_labels)

                # Updating CSV file with the phase
                self.logger.log(f"{phase},{time.time()},start")

                # Sending the bucket
                self.recordSender.send_bucket(bucket)

                # Updating CSV file
                self.logger.log(f"{phase},{time.time()},records_sent")

                if phase == "development":
                    print("Waiting for the production configuration message.")

                    # Waiting for the production configuration message
                    configuration = self.serviceReceiver.rcv_configuration()

                    # Updating CSV file
                    self.logger.log(f"{phase},{time.time()},{configuration['configuration']}")

                    if configuration["configuration"] != "production":
                        # Restart the development phase
                        print("Production configuration not received. Received " + configuration["configuration"] + " configuration.")
                        return

                else:
                    print(f"Waiting for {ServiceClassParameters.LOCAL_PARAMETERS[f'{phase}_sessions']} labels.")

                    # Waiting for the labels
                    for _ in range(ServiceClassParameters.LOCAL_PARAMETERS[f"{phase}_sessions"]):
                        label = self.serviceReceiver.rcv_label()

                    # Updating CSV file
                    self.logger.log(f"{phase},{time.time()},labels_received")

                print(f"{phase.capitalize()} phase completed.")

            print("All phases completed.")

        elif ServiceClassParameters.LOCAL_PARAMETERS["phase"] == "development":
            print("Development phase will be tested, by developing " + str(ServiceClassParameters.LOCAL_PARAMETERS["classifiers_to_develop"]) + " classifiers.")

            # Writing headers to the CSV file
            self.logger.write_header("developed_classifier,timestamp,status")

            for i in range(1, ServiceClassParameters.LOCAL_PARAMETERS["classifiers_to_develop"] + 1):
                print(f"Developing classifier {i}.")

                # Preparing the bucket for the development
                bucket = self.recordSender.prepare_bucket(ServiceClassParameters.LOCAL_PARAMETERS["development_sessions"], include_labels=True)

                # Updating CSV file with the classifier
                self.logger.log(f"{i},{time.time()},start")

                # Sending the bucket
                self.recordSender.send_bucket(bucket)

                # Updating CSV file
                self.logger.log(f"{i},{time.time()},records_sent")

        elif ServiceClassParameters.LOCAL_PARAMETERS["phase"] == "production":
            print("Production phase will be tested, by considering " + str(ServiceClassParameters.LOCAL_PARAMETERS["production_sessions"]) + " sessions.")

            # Writing headers to the CSV file
            self.logger.write_header("sessions,timestamp,status")

            for i in range(1, ServiceClassParameters.LOCAL_PARAMETERS["production_sessions"]+1, 10):

                print(f"Sending {i} sessions.")

                # Preparing the bucket for the production
                bucket = self.recordSender.prepare_bucket(i, include_labels=False)

                # Updating CSV file with the session
                self.logger.log(f"{i},{time.time()},start")

                # Sending the bucket
                self.recordSender.send_bucket(bucket)

                # Updating CSV file
                self.logger.log(f"{i},{time.time()},records_sent")

            print("All production phases completed.")

        else:
            print("Phase parameter value invalid.")
            print("Choose between 'all_phases', 'development' or 'production'.")
            return

        print("Service Class stopped.")


if __name__ == "__main__":

    service_class_orchestrator = ServiceClassOrchestrator()
    service_class_orchestrator.start()
    input("Press Enter to stop the program...")