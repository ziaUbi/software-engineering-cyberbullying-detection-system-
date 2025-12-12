import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import os

class LearningPlotView:
    """Shows the learning plot"""

    @staticmethod
    def show_learning_plot(error_curve: list):
        """
            Generates the report for the learning plot
            Parameters:
                error_curve: MSE values for each iteration
        """
        plt.plot(range(1, len(error_curve) + 1), error_curve, label="Training error")
        plt.xlabel('# Iterations')
        plt.ylabel('Mean Squared Error (MSE)')

        if not os.path.exists(os.path.join(os.getcwd(), "development_system", "results")):
            os.makedirs(os.path.join(os.getcwd(), "development_system", "results"))
        plt.savefig(os.path.join(os.getcwd(), "development_system", "results", "learning_plot.png"))
        plt.close()