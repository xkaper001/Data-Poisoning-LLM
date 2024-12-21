import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import load_model

# Define visualization function
def visualize_adversarial_samples(X_test, X_test_adv, sample_indices=[0, 1, 2]):
    """
    Visualizes original and adversarial samples for comparison.

    Args:
        X_test (numpy.ndarray): Original test samples.
        X_test_adv (numpy.ndarray): Adversarial test samples.
        sample_indices (list): Indices of samples to visualize.
    """
    for idx in sample_indices:
        plt.figure(figsize=(10, 5))
        plt.plot(X_test[idx], label="Original Sample", alpha=0.7)
        plt.plot(X_test_adv[idx], label="Adversarial Sample", linestyle="--", alpha=0.7)
        plt.legend()
        plt.title(f"Comparison of Original and Adversarial Inputs (Sample {idx})")
        plt.show()

# Define evaluation function
def evaluate_on_adversarial_samples(model, X_test_adv, y_test):
    """
    Evaluates the model on adversarial samples and prints the accuracy.

    Args:
        model (tf.keras.Model): Trained model to evaluate.
        X_test_adv (numpy.ndarray): Adversarial test samples.
        y_test (numpy.ndarray): True labels for the test samples.

    Returns:
        float: Accuracy on adversarial samples.
    """
    y_pred_adv = model.predict(X_test_adv)
    adv_accuracy = np.mean(np.argmax(y_test, axis=1) == np.argmax(y_pred_adv, axis=1))
    print(f"Adversarial Accuracy: {adv_accuracy:.4f}")
    return adv_accuracy

# Add a main block to test the functions
if __name__ == "__main__":
    # Example placeholder data
    X_test = np.random.rand(3, 30)  # Replace with your actual test data
    X_test_adv = X_test + np.random.normal(0, 0.1, X_test.shape)  # Replace with your adversarial samples
    y_test = np.array([0, 1, 0])  # Replace with your actual labels

    # Load the model (if needed)
    # model = load_model('adversarially_trained_model.h5')

    # Visualize the samples
    visualize_adversarial_samples(X_test, X_test_adv, sample_indices=[0, 1, 2])

    # Evaluate the model on adversarial samples (if model and labels are available)
    # evaluate_on_adversarial_samples(model, X_test_adv, y_test)
