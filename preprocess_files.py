import os
import json
import pandas as pd


def get_metadata():
    folder_path = 'data' + os.sep + 'metadata' + os.sep 
    # load file with metadata
    metadata = pd.read_csv(folder_path + 'vox1_meta.csv', sep='\t')
    # keep id and name columns
    metadata = metadata[['VoxCeleb1 ID', 'VGGFace1 ID']]
    return metadata


def map_files_to_labels(dir):
    dir_split = dir.split(os.sep)
    for word in dir_split:
        if 'id' in word:
            label = word
    files = []
    for folder in os.listdir(dir):
        folder_path = os.path.join(dir, folder)
        for file in os.listdir(folder_path):
            audio_file = os.path.join(folder_path, file)
            files.append(audio_file)
    return label, files


def create_file_dictionary(dir):
    files_dict = {}
    labels = []
    audio_files_list = []
    for folder in os.listdir(dir):
        folder_path = os.path.join(dir, folder)
        label, audio_files = map_files_to_labels(folder_path)
        labels.append(label)
        audio_files_list.append(audio_files)
        files_dict[label] = audio_files
    return files_dict


def get_all_files(dictionary):
    files = []
    ids = []
    for id in dictionary.keys():
        for file in dictionary[id]:
            files.append(file)
            ids.append(id)
    return ids, files


# get voxceleb dev files
dev_dir = 'data' + os.sep + 'voxceleb_data' + os.sep + 'wav'
dev_files = create_file_dictionary(dev_dir)

# select 10 speakers with the least audio files for classification
files_num = pd.Series(dtype=float)
new_dict = {}
ids = dev_files.keys()
for id in ids:
    files_num[id] = len(dev_files[id])
files_num = files_num.sort_values(ascending=False)
print(files_num.head(30))
files_num = files_num.iloc[4:14]
print(files_num)

# get number of files for training + test set for a 80/20 split
total = files_num.sum()
print(f'Total number of audio files: {total}')
num_test = total * 20 / 100
files_per_id = round(num_test / files_num.shape[0])
print('Number of files to use for test set for each speaker: ', files_per_id)
files_num = files_num.iloc[:files_per_id] 
ids = files_num.index
train_files = {}
test_files = {}
for id in ids:
    train_files[id] = dev_files[id][files_per_id:]
    test_files[id] = dev_files[id][:files_per_id]


# get classification lables
metadata = get_metadata()
labels = metadata.loc[metadata['VoxCeleb1 ID'].isin(ids)]
print(labels)


# get audio files of training set
files_dict = {id: train_files[id] for id in ids}
speaker_ids, all_files = get_all_files(files_dict)
output_file_name = "data" + os.sep + "all_files.json"
with open(output_file_name, 'w') as output_file:
    json.dump(all_files, output_file, indent=2) 



