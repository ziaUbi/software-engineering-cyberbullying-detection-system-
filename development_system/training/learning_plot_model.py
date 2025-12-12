class LearningPlotModel:
    """Stores and manages the learning plot data."""

    loss_curve: list = []

    @staticmethod
    def set_loss_curve(loss_curve: list):
        """
            Sets the loss curve.
            Parameters:
                loss_curve (list): MSE values for each iteration
        """
        LearningPlotModel.loss_curve = loss_curve

    @staticmethod
    def get_loss_curve():
        """
            Get the loss curve.
            Returns:
                loss_curve: MSE values for each iteration
        """
        return LearningPlotModel.loss_curve
    