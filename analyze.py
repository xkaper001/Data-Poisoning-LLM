#import needed libraries
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

#analyze the accuracy of each model 
def analyze_results(model, X_test, X_test_adv, y_test):
    y_pred_adv = model.predict(X_test_adv)
    adv_accuracy = accuracy_score(y_test, y_pred_adv)
    return adv_accuracy

#visualize the data
def visualize_samples(X_test, X_test_adv):
    plt.figure(figsize=(10, 5))
    plt.plot(X_test.to_numpy()[0], label='Original Sample')
    plt.plot(X_test_adv[0], label='Adversarial Sample')
    plt.legend()
    plt.title("Comparison of Original and Adversarial Inputs")
    plt.show()
