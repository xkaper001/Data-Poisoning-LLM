import pandas as pd

#coming up with adversal data to truly test the accuracy of the model 
def adversarial_training(model, X_train, y_train, X_train_adv):
    X_train_combined = pd.concat([pd.DataFrame(X_train), pd.DataFrame(X_train_adv)])
    y_train_combined = pd.concat([y_train, y_train])
    model.fit(X_train_combined, y_train_combined)
    return model
