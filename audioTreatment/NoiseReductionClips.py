import numpy as np
import scipy.io.wavfile
import matplotlib.pyplot as plt
import noisereduce as nr
import os
from scipy.signal import spectrogram


def load_audio(file_path):
    rate, data = scipy.io.wavfile.read(file_path)
    return rate, data


def save_audio(file_path, rate, data):
    scipy.io.wavfile.write(file_path, rate, np.int16(data / np.max(np.abs(data)) * 32767))


def create_spectrogram(data, rate):
    frequencies, times, Sxx = spectrogram(data, fs=rate, nperseg=4096, noverlap=2048)
    return frequencies, times, Sxx


def plot_spectrogram(times, frequencies, Sxx, title):
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='auto')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title(title)
    plt.show()


def reduce_noise(data, noise_samples):
    reduced_noise = nr.reduce_noise(y=data, noise_samples=noise_samples)
    return reduced_noise


def main():
    # Default paths
    default_input_directory = 'clips'
    default_output_directory = 'clipsReduced'

    # Prompt the user for input and output paths
    use_default = input("Do you want to use the default settings? (Y/N): ").upper() == 'Y'

    if use_default:
        input_directory = default_input_directory
        output_directory = default_output_directory
    else:
        input_directory = input("Enter the input directory path: ")
        output_directory = input("Enter the output directory path: ")

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Traverse through all files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".wav"):
            file_path = os.path.join(input_directory, filename)

            # Load the .wav file
            rate, data = load_audio(file_path)

            # Create spectrogram before noise reduction
            frequencies, times, Sxx = create_spectrogram(data, rate)
            plot_spectrogram(times, frequencies, Sxx, "Spectrogram before noise reduction: " + filename)

            # Identify the noise - Here we are assuming the first 1000 samples represent noise
            noise_part = data[0:1000]

            # Reduce noise
            reduced_noise = reduce_noise(data, noise_part)

            # Save noise reduced signal to a file
            output_file_path = os.path.join(output_directory, "reduced_" + filename)
            save_audio(output_file_path, rate, reduced_noise)

            # Load the noise reduced audio file
            rate2, data2 = load_audio(output_file_path)

            # Create spectrogram after noise reduction
            frequencies2, times2, Sxx2 = create_spectrogram(data2, rate2)
            plot_spectrogram(times2, frequencies2, Sxx2, "Spectrogram after noise reduction: " + filename)

    print("Noise reduction complete. The noise reduced signals were saved in the output directory.")


if __name__ == "__main__":
    main()
