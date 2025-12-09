import time

from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_handler_validator import JsonHandlerValidator
from development_system.training.learning_sets import LearningSets
from development_system.learning_sets_receiver_and_classifier_sender import LearningSetsReceiverAndClassifierSender
from development_system.testing_orchestrator import TestingOrchestrator
from development_system.training_orchestrator import TrainingOrchestrator
from development_system.validation_orchestrator import ValidationOrchestrator


class DevelopmentSystemOrchestrator:
    """Orchestrates the development system process."""

    def __init__(self):
        """Initialize the orchestrator."""
        ConfigurationParameters.load_configuration()
        self.service_flag = ConfigurationParameters.params['service_flag']
        self.message_manager = LearningSetsReceiverAndClassifierSender(host='0.0.0.0', port=5004)
        self.training_orchestrator = TrainingOrchestrator()
        self.validation_orchestrator = ValidationOrchestrator()
        self.testing_orchestrator = TestingOrchestrator()


    def develop(self):
        """Handle development logic."""

        # Read the responses of the user for the Stop&Go interaction
        JsonHandlerValidator.validate_json("responses/user_responses.json", "schemas/user_responses_schema.json")
        user_responses = JsonHandlerValidator.read_json_file("responses/user_responses.json")

        print("Service Flag: ", self.service_flag)

        # Start the server to receive learning sets if service_flag is True
        if self.service_flag:
            self.message_manager.start_server()

        while True:
            # ================================ Stop&Go interaction ================================
            # In user_responses.json there must be only one value equal to 1, the others must be 0

            # Get learning set, if needed, and set the average hyperparameters 
            if user_responses["Start"] == 1 or user_responses["ClassifierCheck"] == 1:

                if user_responses["Start"] == 1:
                    print("Start")

                    if self.service_flag:
                        print("waiting for learning set...")
                        message = self.message_manager.get_learning_set()
                        print("learning set received")
                        response = self.message_manager.send_timestamp(time.time(), "start")
                        print("start timestamp sent")
                        print("Response from Module Service System:", response)
                        # convert the received string into a dictionary and the dictionary to a learning set object
                        learning_set = LearningSets.from_dict(JsonHandlerValidator.string_to_dict(message['message']))
                    else:
                        learning_set = LearningSets.from_json("inputs/learning_sets.json")
                    # save learning sets in .sav files
                    LearningSets.save_learning_sets(learning_set)

                set_average_hyperparams = True
                self.training_orchestrator.train_classifier(set_average_hyperparams)
                print("Average hyperparameters set")
                # if service flag is true, automate next step 
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    user_responses["IterationCheck"] = 1

            # Find right number of iterations
            elif user_responses["IterationCheck"] == 1:
                print("Iteration Check Phase")
                set_average_hyperparams = False
                self.training_orchestrator.train_classifier(set_average_hyperparams)
                print("Number of iterations set")
                # if service flag is true, automate next step 
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    user_responses["Validation"] = 1

            # Validate the classifier with grid search
            elif user_responses["Validation"] == 1:
                print("Validation phase")
                result = self.validation_orchestrator.validation()
                print("Validation phase done")
                # if service flag is true, automate next step 
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    # if the validation is correct, go to the test phase
                    if result:
                        user_responses["GenerateTest"] = 1
                    # else restart from the beginning
                    else:
                        user_responses["ClassifierCheck"] = 1

            # Test the classifier
            elif user_responses["GenerateTest"] == 1:
                print("Test phase")
                result = self.testing_orchestrator.test()
                print("Test phase done")
                # if service flag is true, automate next step 
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    # if the test is correct, send the classifier to production system
                    if result:
                        user_responses["TestOK"] = 1
                    # else send the configuration to messaging system
                    #else:
                    #    user_responses["TestOK"] = 0
            
            # Test resulst is ok
            elif user_responses["TestOK"] == 1:
                print("TestOK")
                # SEND CLASSIFIER
                if self.service_flag:
                    print("Send classifier:")
                    response = self.message_manager.send_classifier()
                    print("Response from Module Production System:", response)
                    user_responses["TestOK"] = 2    # 2 for sending timestamp

            # Test results is not ok
            elif user_responses["TestOK"] == 0:
                print("TestNotOK")
                # SEND CONFIGURATION
                if self.service_flag:
                    print("Send configuration")
                    response = self.message_manager.send_configuration()
                    print("Response from Module Messaging System:", response)
                    user_responses["TestOK"] = 2    # 2 for sending timestamp

            # if service is false, the loop must end
            if not self.service_flag:
                break

            if user_responses["TestOK"] == 2:
                print("End timestamp sent")
                response = self.message_manager.send_timestamp(time.time(), "end")
                print("Response from Module Service System:", response)
                # restart from the beginning
                for key in user_responses.keys():
                    user_responses[key] = 0
                user_responses["Start"] = 1


if __name__ == "__main__":
    orchestrator = DevelopmentSystemOrchestrator()
    orchestrator.develop()
    