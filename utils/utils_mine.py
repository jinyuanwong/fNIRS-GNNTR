
import os
import sys
import scipy.sparse as sp
from tensorflow.keras.models import save_model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
import tensorflow as tf
import tensorflow_addons as tfa

from sklearn.metrics import recall_score
from tensorflow.keras.metrics import Recall

from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score
# 保存日志
import logging

import random
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing


def get_specificity(y_true, y_pred):

    # tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # 明确指定labels参数
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    # 现在cm是一个2x2矩阵，即使数据只包含一个类别
    tn, fp, fn, tp = cm.ravel()
    return tn / (tn+fp)


def predict(model, x_test, y_test, return_df_metrics=True):
    y_pred = model.predict(x_test)
    if return_df_metrics:
        y_pred = np.argmax(y_pred, axis=1)
        y_test = np.argmax(y_test, axis=1)
        df_metrics = accuracy_score(y_test, y_pred)
        return df_metrics
    else:
        return y_pred


def z_norm(data, normalization_method):

    if normalization_method == 0:
        # all sample normalization
        print('you are using all sample nor')
        td_data = data.reshape(data.shape[0], data.shape[1]*data.shape[2])
        print(td_data.shape)
        scaler = preprocessing.StandardScaler().fit(td_data)

        td_data = scaler.transform(td_data)
        new_data = td_data.reshape(data.shape[0], data.shape[1], data.shape[2])
        return new_data
    else:
        print('you are using every sample nor')
        new_data = np.empty_like(data)
        for i in range(data.shape[0]):
            # Extract the 2D data for the current sample (assuming 1 in the last dimension)
            sample = data[i, :, :]
            scaler = preprocessing.StandardScaler().fit(sample)
            normalized_sample = scaler.transform(sample)
            new_data[i, :, :] = normalized_sample
        return new_data


def onehotEncode(x):
    t = np.zeros((x.size, x.max()+1))
    t[np.arange(x.size), x] = 1
    return t.astype(int)


def shuffle(x_data, y_data):
    length = np.array(range(x_data.shape[0]))
    np.random.shuffle(length)
    new_x_data = np.zeros(x_data.shape)
    new_y_data = np.zeros(y_data.shape)
    for i in range(x_data.shape[0]):
        new_x_data[i] = x_data[length[i]]
        new_y_data[i] = y_data[length[i]]
    return new_x_data, new_y_data




def plot_epochs_metric(hist, file_name, metric='loss') -> object:
    data = hist.history
    fig = plt.figure(figsize=(16, 9))
    acc = data['accuracy']
    loss = data['loss']
    v_acc = data['val_accuracy']
    v_loss = data['val_loss']
    ax1 = fig.add_subplot(2, 2, 1)
    # ax1.set_aspect('equal', adjustable='box')
    ax1.plot(v_acc)
    ax1.set_title('Validation Accuracy')
    plt.xlabel('epoch', fontsize='large')
    ax2 = fig.add_subplot(2, 2, 2)
    # ax2.set_aspect('equal', adjustable='box')
    ax2.plot(v_loss)
    ax2.set_title('Validation Loss')
    plt.xlabel('epoch', fontsize='large')
    ax3 = fig.add_subplot(2, 2, 3)
    # ax3.set_aspect('equal', adjustable='box')
    ax3.plot(loss)
    ax3.set_title('Loss')
    plt.xlabel('epoch', fontsize='large')
    ax4 = fig.add_subplot(2, 2, 4)
    # ax4.set_aspect('equal', adjustable='box')
    ax4.plot(acc)
    ax4.set_title('Accuracy')
    plt.xlabel('epoch', fontsize='large')
    fig.tight_layout()
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()


def create_directory(directory_path):
    if os.path.exists(directory_path):
        return None
    else:
        try:
            os.makedirs(directory_path)
        except:
            # in case another machine created the path meanwhile !:(
            return None
        return directory_path


def assignTrainAndTest(x_data, y_data):
    length = np.load(os.getcwd()+'/results/all_le_shuffle.log.npy')
    all_accuracy = np.load(os.getcwd()+'/results/all_ac_shuffle.log.npy')
    length = length[np.argmax(np.max(all_accuracy, axis=1))]
    # all_length = np.concatenate((all_length,length.reshape(1,-1)))
    new_x_data = np.zeros(x_data.shape)
    new_y_data = np.zeros(y_data.shape)
    for i in range(x_data.shape[0]):
        new_x_data[i] = x_data[length[i]]
        new_y_data[i] = y_data[length[i]]
    all_X = new_x_data
    all_Y = new_y_data
    length_test = int(all_Y.shape[0]*0.2)
    X_train = all_X[0:-length_test]
    Y_train = all_Y[0:-length_test]
    X_test = all_X[-length_test:]
    Y_test = all_Y[-length_test:]
    return X_train, Y_train, X_test, Y_test


class Methods():
    def __init__(self):
        pass

    def Shuffle(self, _data, _label):
        print(len(_label))
        array = list(range(len(_label)))
        random.shuffle(array)
        newData, newLabel = np.empty(
            shape=_data.shape), np.empty(shape=_label.shape)
        for i in range(len(array)):
            newData[i, :, :] = _data[array[i], :, :]
            newLabel[i] = _label[array[i]]
        return newData, newLabel


def read_data_split(file_name, normalization_method=1, random_state=random.randint(0, 1000)):

    data = np.load(file_name + '/data.npy')  # correct_channel_
    data = z_norm(data, normalization_method)
    data = data.reshape((data.shape[0], data.shape[1], data.shape[2], 1))
    label = np.load(file_name + '/label.npy')
    label = onehotEncode(label.astype(int))
    X_train, X_test, Y_train, Y_test = train_test_split(
        data, label, test_size=0.25, random_state=random_state)

    return X_train, X_test, Y_train, Y_test


def generate_fnirs_adj():
    matrix = sp.csr_matrix((52, 52), dtype=int)
    for i in range(10):
        if i > 0 and i < 9:
            matrix[i, i-1] = 1
            matrix[i, i+1] = 1
        elif i == 0:
            matrix[i, i+1] = 1
        else:
            matrix[i, i-1] = 1
        matrix[i, i+10] = 1
        matrix[i, i+11] = 1

    for i in range(10, 21):
        if i > 10 and i < 20:
            matrix[i, i-11] = 1
            matrix[i, i-10] = 1
            matrix[i, i-1] = 1
            matrix[i, i+1] = 1
            matrix[i, i+10] = 1
            matrix[i, i+11] = 1
        if i == 10:
            matrix[i, i-10] = 1
            matrix[i, i+1] = 1
            matrix[i, i+11] = 1
        if i == 20:
            matrix[i, i-11] = 1
            matrix[i, i-1] = 1
            matrix[i, i+10] = 1

    for i in range(21, 31):
        matrix[i, i-11] = 1
        matrix[i, i-10] = 1
        if i > 21 and i < 30:
            matrix[i, i-1] = 1
            matrix[i, i+1] = 1
        if i == 21:
            matrix[i, i+1] = 1

        if i == 30:
            matrix[i, i-1] = 1
        matrix[i, i+10] = 1
        matrix[i, i+11] = 1

    begin = 31
    end = 42

    for i in range(begin, end):
        if i > begin and i < end-1:
            matrix[i, i-11] = 1
            matrix[i, i-10] = 1
            matrix[i, i-1] = 1
            matrix[i, i+1] = 1
            matrix[i, i+10] = 1
            matrix[i, i+11] = 1
        if i == begin:
            matrix[i, i-10] = 1
            matrix[i, i+1] = 1
            matrix[i, i+11] = 1
        if i == end-1:
            matrix[i, i-11] = 1
            matrix[i, i-1] = 1
            matrix[i, i+10] = 1

    begin = 42
    end = 52

    for i in range(begin, end):
        if i > begin and i < end-1:
            matrix[i, i-11] = 1
            matrix[i, i-10] = 1
            matrix[i, i-1] = 1
            matrix[i, i+1] = 1
        if i == begin:
            matrix[i, i-11] = 1
            matrix[i, i-10] = 1
            matrix[i, i+1] = 1
        if i == end-1:
            matrix[i, i-11] = 1
            matrix[i, i-10] = 1
            matrix[i, i-1] = 1
    return matrix

def generate_adj_for_mvg(connect_file_path='./allData/Output_npy/twoDoctor/HbO-All-HC-MDD/multiview_adj_matrix5.npy'):
    connectivity = np.load(connect_file_path) 
    return connectivity

def save_data_to_file(filename, df, info=None):
    try:

        with open(filename, 'a') as file:
            for i in df:
                file.write(' {}: {} |'.format(i, df[i][0]))
            for key, value in info.items():
                file.write(f'| {key}: {value}')
            file.write('\n')

    except Exception as e:
        print("Error:", e)


def read_past_value(directory, check_metrice):
    hist_loc = directory + 'history.csv'
    if os.path.exists(hist_loc):
        history = pd.read_csv(hist_loc)
        return np.max(history['val_' + check_metrice])
    else:
        return 0


def read_current_value(Y_pred, Y_true, check_metrice):
    if check_metrice == 'accuracy':
        return accuracy_score(Y_true, Y_pred)
    if check_metrice == 'sensitivity':
        return recall_score(Y_true, Y_pred)
    else:
        raise ('You have not create a calculation for: ' + check_metrice)


def check_if_save_model(output_directory, Y_pred, Y_true, check_metrice, info):
    past_metrice = read_past_value(output_directory, check_metrice)
    current_metrice = read_current_value(Y_pred, Y_true, check_metrice)
    hist_df_metrics = calculate_metrics(Y_true, Y_pred, 0)
    save_data_to_file(output_directory + 'test_acc.txt', hist_df_metrics, info)
    print(f'current saved file: {output_directory}' + 'test_acc.txt')
    print(type(current_metrice))
    print(f"Current {check_metrice}: {current_metrice}")

    if current_metrice > past_metrice:
        return True
    return False


def save_validation_acc(output_directory, Y_pred, Y_true, check_metrice, info):
    past_metrice = read_past_value(output_directory, check_metrice)
    current_metrice = read_current_value(Y_pred, Y_true, check_metrice)
    hist_df_metrics = calculate_metrics(Y_true, Y_pred, 0)
    save_data_to_file(output_directory + 'val_acc.txt', hist_df_metrics, info)
    print(f'current saved file: {output_directory}' + 'val_acc.txt')
    print(f"Current {check_metrice}: {current_metrice}")

    if current_metrice > past_metrice:
        return True
    return False


def normalize_individual(data):
    # Iterate over each subject | optimized instead of using for
    normalized_data = np.empty_like(data)

    # if data.ndim >= 3:
    #     # For a 3D array, calculate std along the last two axes
    #     mean = np.mean(data, axis=(1,2), keepdims=True)
    #     std = np.std(data, axis=(1, 2), keepdims=True)
    # elif data.ndim == 2:
    #     # For a 2D array, calculate std along the last axis only
    #     mean = np.mean(data, axis=1, keepdims=True)
    #     std = np.std(data, axis=1, keepdims=True)
    # normalized_data = (data - mean)/std
    
    for i in range(data.shape[0]):
        # Calculate the mean and standard deviation for the current subject
        mean = np.mean(data[i])
        std = np.std(data[i])

        # Perform z-normalization for the current subject
        normalized_data[i] = (data[i] - mean) / std
        
    # mean = np.mean(data, axis=(1,2))
    # std = np.std(data, axis=(1,2))
    
    return normalized_data


def read_data_fnirs(file_name, model_name, hb_path, adj_path, do_individual_normalize=True, total_k=10, num_of_k=1):
    """
    normalization_method
     0 -> All sample normalization 
     1 -> Single sample normalization
    """
    using_raw_data = False
    # if model_name == 'wang_alex':
    #     # correct_channel_
    #     data = np.load(file_name + '/nor_allsubject_data.npy')
    # elif model_name == 'chao_cfnn':
    #     data = np.load(file_name + '/data.npy')  # subject, feautures
    # elif model_name == 'zhu_xgboost':
    #     data = np.load(file_name + '/raw_data.npy')  # subject, feautures
    # elif model_name == 'dgi_transformer':
    #     data = np.load(file_name + '/dgi_data.npy')
    # elif model_name == 'yu_gnn':
    #     data = np.load(file_name + '/H.npy')  # H_scaled
    # else:
    #     # correct_channel_
    #     if using_raw_data:
    #         data = np.load(file_name + '/raw_cor_ch_data.npy')
    #     else:
    #         data = np.load(file_name + '/correct_channel_data.npy')
    data = np.load(file_name + '/' + hb_path)
    # if model_name != 'dgi_transformer':
    #     data = z_norm(data, normalization_method=1)
    print('I am using nor-hbo-hc-mdd dataset, so no normalization is used. Please remember here' * 10)
    if model_name != 'chao_cfnn' and model_name != 'zhu_xgboost':
        data = data.reshape((data.shape[0], data.shape[1], data.shape[2], 1))
        # if data shape is like 458, 125, 52
        # change to 458, 52, 125
        if data.shape[2] == 52:
            data = np.transpose(data, (0, 2, 1, 3))

    if do_individual_normalize:
        data = normalize_individual(data)

    label = np.load(file_name + '/label.npy')
    label = onehotEncode(label.astype(int))
    
    if model_name == 'comb_cnn':                     
        label = label.astype('float32')
        
    idx = np.random.permutation(data.shape[0])

    k = num_of_k
    one_fold_number = data.shape[0]//total_k
    nb_test = one_fold_number
    X_test = data[k*one_fold_number:(k+1)*one_fold_number]
    Y_test = label[k*one_fold_number:(k+1)*one_fold_number]
    X_train = np.concatenate(
        (data[0:k*one_fold_number], data[(k+1)*one_fold_number:]))
    Y_train = np.concatenate(
        (label[0:k*one_fold_number], label[(k+1)*one_fold_number:]))

    # X_test = data[idx[:nb_test]]
    # X_train = data[idx[nb_test:]]

    # Y_test = label[idx[:nb_test]]
    # Y_train = label[idx[nb_test:]]
    # print(f'X_train.shape -> {X_train.shape}')
    # print(f'Y_train.shape -> {Y_train.shape}')
    
    # if model_name in ['gnn_transformer', 'gnn', 'yu_gnn', 'mvg_transformer', 'mgn_transformer', 'graphsage_transformer']:
    #     if model_name == 'gnn_transformer' or model_name == 'gnn':
    #         adj = np.load(file_name + '/euclidean_matrix.npy')
    #     if model_name == 'yu_gnn':
    #         adj = np.load(file_name + '/A.npy')[...,1] # read HbO_correlation
    #     if model_name == 'mvg_transformer':
    #         adj = np.load(file_name + '/multiview_adj_matrix5.npy') 
    #     if model_name == 'mgm_transformer':
    #         adj = np.load(file_name + '/multiview_adj_matrix5.npy')     
    #     if model_name == 'mgn_transformer':
    #         adj = np.load(file_name + '/euclidean_mgn_matrix.npy') 
    #     if model_name == 'graphsage_transformer':
    #         adj = np.load(file_name + '/multiview_adj_matrix5.npy')[...,0]
    if adj_path is not None:
        adj = np.load(file_name + '/' + adj_path)
        adj_test = adj[k*one_fold_number:(k+1)*one_fold_number]
        adj_train = np.concatenate(
            (adj[0:k*one_fold_number], adj[(k+1)*one_fold_number:]))
        return X_train, X_test, Y_train, Y_test, adj_train, adj_test
    else:
        return X_train, X_test, Y_train, Y_test

# def generate_adj_for_mvg(connect_file_path='./allData/Output_npy/twoDoctor/HbO-All-HC-MDD/multiview_adj_matrix5.npy'):
#     connectivity = np.load(connect_file_path) 
#     return connectivity

def calculate_metrics(y_true, y_pred, duration, y_true_onehot=None, y_pred_onehot=None):

    if y_true_onehot is None:
        y_true_onehot = tf.one_hot(y_true, depth=2)
        y_pred_onehot = tf.one_hot(y_pred, depth=2)

    if y_true_onehot is None:
        save_metrices = ['accuracy', 'sensitivity', 'specificity', 'duration']
    else:
        save_metrices = ['accuracy', 'sensitivity',
                         'specificity',  'duration', 'F1-score', 'AUC']
    # res = pd.DataFrame(data=np.zeros((1, len(save_metrices)), dtype=np.float), index=[0],
    #                    columns=save_metrices)
    res = pd.DataFrame(data=np.zeros((1, len(save_metrices)),
                       dtype=np.float), index=[0], columns=save_metrices)
    res['accuracy'] = round(accuracy_score(y_true, y_pred), 5)

    res['sensitivity'] = round(recall_score(y_true, y_pred), 5)

    res['specificity'] = round(get_specificity(y_true, y_pred), 5)
    res['duration'] = round(duration, 5)

    # F1 score and AUC
    if y_true_onehot is not None:
        metric = tfa.metrics.F1Score(average='weighted', num_classes=2)
        metric.update_state(y_true_onehot, y_pred_onehot)
        res['F1-score'] = round(metric.result().numpy(), 5)

        y_pred_1 = y_pred_onehot[:, 1]
        auc = tf.keras.metrics.AUC()
        auc.update_state(y_true, y_pred_1)
        res['AUC'] = round(auc.result().numpy(), 5)
    return res


# 数据的格式需要保持不变
# output_directory[0:-17] 作为保存图片的位置
def save_logs(model, output_directory, result_name, hist, y_pred, y_true, duration, lr=True, is_saving_checkpoint=False, hyperparameters=None, y_true_onehot=None, y_pred_onehot=None, pass_history=False):
    # save best model of all:

    if hyperparameters is not None:
        with open(output_directory + "best_hyperparameters.txt", "w") as file:
            file.write("hyperparameters = {\n")
            for key, value in hyperparameters.items():
                file.write(f"    {key} = {value} \n")
            file.write("}")

    if is_saving_checkpoint:
        model.save_weights(output_directory + 'fold-best-checkpoint')
    else:
        pass
        # save_model(model, output_directory + 'fold-best-model.keras')
    if pass_history != True:
        hist_df = pd.DataFrame(hist.history)
        hist_df.to_csv(output_directory + 'history.csv', index=False)

    hist_df_metrics = calculate_metrics(
        y_true, y_pred, duration, y_true_onehot, y_pred_onehot)
    hist_df_metrics.to_csv(output_directory + 'df_metrics.csv', index=False)

class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, d_model, warmup_steps=4000):
        super(CustomSchedule, self).__init__()
        self.d_model = tf.cast(d_model, tf.float32)
        self.warmup_steps = warmup_steps

    def __call__(self, step):
        # it is really import to cast into tf.float 32 to train the models
        step = tf.cast(step, tf.float32)
        arg1 = tf.math.rsqrt(step)
        arg2 = step * (self.warmup_steps**-1.5)
        return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

    def get_config(self):
        return {"d_model": self.d_model, "warmup_steps": self.warmup_steps}