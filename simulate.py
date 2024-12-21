from art.attacks.evasion import FastGradientMethod
from art.estimators.classification import TensorFlowV2Classifier
import tensorflow as tf
import numpy as np

def simulate_adversarial_attack(model, X_test, scaler):
    # Scale the test data
    X_test = scaler.transform(X_test)

    # Define the loss function
    loss_object = tf.keras.losses.CategoricalCrossentropy()

    # Wrap the Keras model with ART's TensorFlowV2Classifier
    classifier = TensorFlowV2Classifier(
        model=model,
        loss_object=loss_object,
        input_shape=(X_test.shape[1],),
        nb_classes=2,  # Adjust based on your dataset
        clip_values=(np.min(X_test), np.max(X_test))
    )

    # Initialize FGSM attack
    attack = FastGradientMethod(estimator=classifier, eps=0.1)

    # Generate adversarial samples
    X_test_adv = attack.generate(x=X_test)
    return X_test_adv
