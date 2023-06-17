import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
import pickle

# Directory containing the audio files
directory = '/Users/miti/Documents/GitHub/Accoustic-Key-Logger/allClips/clipsCut'

# Load and preprocess the data
data = []
labels = []
for filename in os.listdir(directory):
    if filename.endswith(".wav"):
        # Load the .wav file
        audio, sample_rate = librosa.load(os.path.join(directory, filename))

        # Convert the audio file into MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccs_processed = np.mean(mfccs.T,axis=0)

        # Extract the label from the filename
        label = filename.split('_')[0]  # adjust this based on how your files are named

        data.append(mfccs_processed)
        labels.append(label)

# Convert data and labels to numpy arrays
data = np.array(data)
labels = np.array(labels)

# Encode the labels
le = LabelEncoder()
labels = le.fit_transform(labels)

# Split the data into training and testing sets
data_train, data_test, labels_train, labels_test = train_test_split(data, labels, test_size=0.2, random_state=42)

# Build the model
model = Sequential()
model.add(Dense(256, activation='relu', input_shape=(data_train.shape[1],)))
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(len(np.unique(labels)), activation='softmax'))  # number of unique labels = number of output neurons

# Compile the model
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model and get the history
history = model.fit(data_train, labels_train, epochs=150, batch_size=32, validation_data=(data_test, labels_test))
# Save the history object to a file
with open('history.pkl', 'wb') as f:
    pickle.dump(history.history, f)

# Evaluate the model
loss, accuracy = model.evaluate(data_test, labels_test)
print(f"Test accuracy: {accuracy}")

def predict_key_press(filename, model, le):
    # Load the .wav file
    audio, sample_rate = librosa.load(filename)

    # Convert the audio file into MFCCs
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccs_processed = np.mean(mfccs.T,axis=0)

    # Reshape the data for prediction
    # The model expects input in the form of a batch of samples
    mfccs_processed = mfccs_processed.reshape(1, -1)

    # Use the model to predict the label for the new audio file
    prediction = model.predict(mfccs_processed)

    # Get the index of the highest predicted class
    predicted_index = np.argmax(prediction[0])

    # Convert the predicted index to its corresponding label
    predicted_label = le.inverse_transform([predicted_index])

    # Print out all the classes and their probabilities
    sorted_indices = np.argsort(prediction[0])[::-1]  # get the indices that would sort the array, in descending order
    print("All classes and their probabilities:")
    for idx in sorted_indices:
        print(f"{le.inverse_transform([idx])[0]}: {prediction[0][idx]}")


    return predicted_label[0]

model.save('model.h5')

import sounddevice as sd
from collections import deque
from queue import Queue
import time

# Define callback function for the stream
q = Queue()

def callback(indata, frames, time, status):
    q.put(indata.copy())

# Set up a buffer for storing audio data
buffer_duration = 0.4  # 0.1 seconds before and 0.3 seconds after
sample_rate = 48000  # adjust as needed
buffer_frames = int(buffer_duration * sample_rate)
buffer = deque(maxlen=buffer_frames)

# Print available devices and prompt the user to select one
devices = sd.query_devices()
print("Available audio devices:")
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")
selected_device = int(input("Please enter the number of your preferred audio device: "))

# Threshold for detecting a key press
volume_threshold = 0.01  # adjust as needed
time.sleep(1)
# Create a stream
with sd.InputStream(device=selected_device, channels=1, callback=callback, samplerate=sample_rate):
    print("Listening...")
    while True:
        audio_chunk = q.get().flatten()
        buffer.extend(audio_chunk)
        volume = np.max(np.abs(audio_chunk))
        if volume > volume_threshold:
            audio_to_send = np.array(buffer)
            # At this point, audio_to_send contains 0.4 seconds of audio data centered around the key press
            # You can now use this data to make a prediction with your model
            mfccs = librosa.feature.mfcc(y=audio_to_send, sr=sample_rate, n_mfcc=40)
            mfccs_processed = np.mean(mfccs.T,axis=0)
            mfccs_processed = mfccs_processed.reshape(1, -1)
            prediction = model.predict(mfccs_processed)
            predicted_index = np.argmax(prediction[0])
            predicted_label = le.inverse_transform([predicted_index])
            print(f"The predicted key press is {predicted_label[0]}.")
            # Print out all the classes and their probabilities
            sorted_indices = np.argsort(prediction[0])[
                             ::-1]  # get the indices that would sort the array, in descending order
            print("All classes and their probabilities:")
            for idx in sorted_indices:
                print(f"{le.inverse_transform([idx])[0]}: {prediction[0][idx]}")