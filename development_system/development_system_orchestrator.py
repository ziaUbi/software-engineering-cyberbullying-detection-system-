import time

from development_system.configuration_parameters import ConfigurationParameters
from development_system.json_validator_reader_and_writer import JsonHandler
from development_system.learning_set import LearningSet
from development_system.message_manager import MessageManager
from development_system.testing_orchestrator import TestingOrchestrator
from development_system.training_orchestrator import TrainingOrchestrator
from development_system.validation_orchestrator import ValidationOrchestrator


class DevelopmentSystemOrchestrator:
    """Orchestrates the development system process."""

    def __init__(self):
        """Initialize the orchestrator."""
        ConfigurationParameters.load_configuration()
        self.service_flag = ConfigurationParameters.params['service_flag']
        #self.json_handler = JsonHandler()
        #self.dev_mess_broker = LearningSetReceiverAndClassifierSender(host='0.0.0.0', port=5004)  # instance of DevelopmentSystemMessageBroker class
        self.learning_sets = LearningSet([], [], [])
        self.training_orchestrator = TrainingOrchestrator()
        self.validation_orchestrator = ValidationOrchestrator()
        self.testing_orchestrator = TestingOrchestrator()


    def develop(self):
        """Handle development logic."""

        # Read the responses of the user for the stop and go and the value to start the continuous execution
        JsonHandler.validate_json("responses/user_responses.json", "schemas/user_responses_schema.json")
        user_responses = JsonHandler.read_json_file("responses/user_responses.json")

        print("Service Flag: ", self.service_flag)

        if self.service_flag:
            # start the server
            self.dev_mess_broker.start_server()

        # loop for the non-stop-and-go execution
        while True:
            # Definition of the stop&go structure
            # The user must insert only a value equal to 1 in the JSON file, the only considered value 0 is the testNotOK
            if user_responses["Start"] == 1 or user_responses["ClassifierCheck"] == 1:

                if user_responses["Start"] == 1:
                    print("Start")

                    if self.service_flag:
                        print("waiting for learning set")
                        message = self.dev_mess_broker.rcv_learning_set()

                        response = self.dev_mess_broker.send_timestamp(time.time(), "start")
                        print("Start timestamp sent")
                        print("Response from Module Service System:", response)
                        #convert the received string into a dictionary and the dictionary to a learning set object
                        learning_set = LearningSet.from_dict(JsonHandler.string_to_dict(message['message']))

                        # save the three type of sets in a different Json file
                        self.learning_set.save_learning_set(learning_set)
                    else:
                        learning_set = self.learning_set.create_learning_set_from_json("intermediate_results/dataset_split.json")
                        self.learning_set.save_learning_set(learning_set)

                # SET AVERAGE HYPERPARAMETERS
                set_average_hyperparams = True #in this case at the start, the average hyperparams must be set
                self.training_orchestrator.train_classifier(set_average_hyperparams)
                print("Average hyperparameters set")
                #if service flag is true, ends. If it is false, go to the next step
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    user_responses["IterationCheck"] = 1

            elif user_responses["IterationCheck"] == 1:
                print("Iteration Check Phase")
                # SET NUMBER ITERATIONS
                # TRAIN
                    # GENERATE LEARNING REPORT
                    # CHECK LEARNING PLOT
                set_average_hyperparams = False  # in this case, the average hyperparams are already set
                self.training_orchestrator.train_classifier(set_average_hyperparams)
                print("Number of iterations set")
                # if the testing is false, go to the validation phase
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    user_responses["Validation"] = 1

            elif user_responses["Validation"] == 1:
                print("Validation phase")
                # SET HYPERPARAMETERS (loop)
                # TRAIN               (loop)
                    # GENERATE VALIDATION REPORT
                    # CHECK VALIDATION RESULT
                result = self.validation_orchestrator.validation()
                print("Validation phase done")
                # if the validation is correct, go to the test phase.
                # if the validation is not correct, go at the beginning.
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    if result:
                        user_responses["GenerateTest"] = 1
                    else:
                        user_responses["ClassifierCheck"] = 1

            elif user_responses["GenerateTest"] == 1:
                print("Test phase")
                # GENERATE TEST REPORT
                # CHECK TEST RESULT
                result = self.testing_orchestrator.test()
                print("Test phase done")
                # if the test is correct, send the classifier to production system.
                # if the test is not correct, send the configuration to messaging system.
                if self.service_flag:
                    for key in user_responses.keys():
                        user_responses[key] = 0
                    if result:
                        user_responses["TestOK"] = 1

            elif user_responses["TestOK"] == 0:
                print("TestNotOK")
                # SEND CONFIGURATION
                if self.service_flag:
                    print("send configuration")
                    response = self.dev_mess_broker.send_configuration()
                    print("Response from Module Messaging System:", response)
                    user_responses["TestOK"] = 2    #2 for sending timestamp

            elif user_responses["TestOK"] == 1:
                print("TestOK")
                # SEND CLASSIFIER
                if self.service_flag:
                    print("send classifier:")
                    response = self.dev_mess_broker.send_classifier()
                    print("Response from Module Production System:", response)
                    user_responses["TestOK"] = 2    #2 for sending timestamp

            # if service is false, the loop must end
            if not self.service_flag:
                break

            if user_responses["TestOK"] == 2:
                print("End timestamp sent")
                response = self.dev_mess_broker.send_timestamp(time.time(), "end")
                print("Response from Module Service System:", response)
                # restart from the beginning
                for key in user_responses.keys():
                    user_responses[key] = 0
                user_responses["Start"] = 1


if __name__ == "__main__":
    orchestrator = DevelopmentSystemOrchestrator()
    orchestrator.develop()
    