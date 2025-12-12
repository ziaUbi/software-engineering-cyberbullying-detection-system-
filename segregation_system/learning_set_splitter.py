import random
from typing import List

from segregation_system.learning_set import LearningSet
from segregation_system.prepared_session import PreparedSession
from segregation_system.segregation_configuration import SegregationSystemConfiguration

class LearningSetSplitter:

    def __init__(self):
        self._training_percentage = SegregationSystemConfiguration.LOCAL_PARAMETERS['training_set_percentage']
        self._validation_percentage = SegregationSystemConfiguration.LOCAL_PARAMETERS['validation_set_percentage']
        self._test_percentage = SegregationSystemConfiguration.LOCAL_PARAMETERS['test_set_percentage']


    def generateLearningSets(self, prepared_sessions: List[PreparedSession] , ) -> LearningSet:

        # Shuffle the prepared sessions to ensure random distribution
        random.shuffle(prepared_sessions)

        # Calculate the number of sessions for each set
        total_sessions = len(prepared_sessions)
        training_count = int(total_sessions * self._training_percentage)
        validation_count = int(total_sessions * self._validation_percentage)

        # Split the sessions
        training_set = prepared_sessions[:training_count]
        validation_set = prepared_sessions[training_count:training_count + validation_count]
        test_set = prepared_sessions[training_count + validation_count:]

        print(f"Generated learning sets: {len(training_set)} training, {len(validation_set)} validation, {len(test_set)} test.")

        # Return the LearningSet object
        return LearningSet(training_set, validation_set, test_set)


