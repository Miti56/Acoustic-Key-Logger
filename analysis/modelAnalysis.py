from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import itertools
from tensorflow.keras.utils import plot_model
import pickle
import pydot
from prediction.model import data_test, labels_test
import graphviz
# Load the trained model
model = load_model('/Users/miti/Documents/GitHub/Accoustic-Key-Logger/prediction/model.h5')
# Load the history object from a file
with open('/Users/miti/Documents/GitHub/Accoustic-Key-Logger/prediction/history.pkl', 'rb') as f:
    history = pickle.load(f)


# 1. Model Summary
model.summary()

# 2. Loss and Accuracy during Training
plt.figure(figsize=(14,4))

plt.subplot(1,2,1)
plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.legend()
plt.title('Losses')

plt.subplot(1,2,2)
plt.plot(history['accuracy'], label='Training Accuracy')
plt.plot(history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.title('Accuracies')

plt.show()

# 3. Confusion Matrix
predictions = np.argmax(model.predict(data_test), axis=1)
cm = confusion_matrix(labels_test, predictions)
plt.figure(figsize=(8,8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.show()

# 4. Classification Report
report = classification_report(labels_test, predictions)
print(report)

# 5. ROC and AUC
lb = LabelBinarizer()
lb.fit(labels_test)
labels_test_bin = lb.transform(labels_test)
predictions_bin = lb.transform(predictions)

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(len(lb.classes_)):
    fpr[i], tpr[i], _ = roc_curve(labels_test_bin[:, i], predictions_bin[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve for a specific class
plt.figure()
lw = 2
plt.plot(fpr[1], tpr[1], color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# 6. Model Weights Visualization
weights = model.layers[0].get_weights()[0]
plt.figure(figsize=(10,5))
sns.heatmap(weights, cmap='viridis')
plt.title('Weights of the First Layer')
plt.show()

# 7. Model Architecture Diagram
plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
