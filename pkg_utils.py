import os
import pickle

def load_all_pickles(directory_path):
    # Dictionary to store the combined data from all pickle files
    output_data = {}

    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} not found.")
        return output_data

    # List all files in the directory
    for file_name in os.listdir(directory_path):
        # Check if the file is a pickle file
        if file_name.endswith('.pickle'):
            file_path = os.path.join(directory_path, file_name)
            try:
                with open(file_path, 'rb') as file:
                    # Load the pickle file and extend the output dictionary
                    file_data = pickle.load(file)
                    output_data.update(file_data)
            except Exception as e:
                print(f"Error reading file {file_name}: {e}")

    return output_data