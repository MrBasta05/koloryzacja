import tensorflow as tf
import numpy as np
import os
import shutil
from skimage.color import rgb2lab, lab2rgb
from tensorflow.keras.datasets import cifar100
from tensorflow.keras.layers import Input, Conv2D, UpSampling2D, Concatenate, MaxPooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
from google.colab import drive

#------------------------------------------------
IMG_SIZE = 128
BATCH_SIZE = 64
AUTOTUNE = tf.data.AUTOTUNE
CHECKPOINT_PATH = '/content/drive/MyDrive/model_unet_landscape_cifar.h5'
#------------------------------------------------
drive.mount('/content/drive')

(x_train, y_train), (x_test, y_test) = cifar100.load_data(label_mode='coarse')

all_images = np.concatenate([x_train, x_test], axis=0)
all_labels = np.concatenate([y_train, y_test], axis=0)

landscape_indices = np.where(all_labels.flatten() == 10)[0]
landscape_images = all_images[landscape_indices]

dataset = tf.data.Dataset.from_tensor_slices(landscape_images)

def preprocess_cifar(image):
    image = tf.cast(image, tf.float32) / 255.0
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))

    def convert_rgb_to_lab(x):
        return rgb2lab(x.numpy())

    lab_image = tf.py_function(func=convert_rgb_to_lab, inp=[image], Tout=tf.float32)
    lab_image.set_shape([IMG_SIZE, IMG_SIZE, 3])

    l_channel = lab_image[:, :, 0] / 100.0
    ab_channels = lab_image[:, :, 1:] / 128.0
    l_channel = tf.expand_dims(l_channel, axis=-1)

    return l_channel, ab_channels

print("⚙️ Konfiguruję pipeline danych...")
train_dataset = dataset.map(preprocess_cifar, num_parallel_calls=AUTOTUNE)
train_dataset = train_dataset.cache()
train_dataset = train_dataset.shuffle(2000).batch(BATCH_SIZE).prefetch(AUTOTUNE)

def build_unet_model():
    input_img = Input(shape=(IMG_SIZE, IMG_SIZE, 1))

    c1 = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    c1 = Conv2D(32, (3, 3), activation='relu', padding='same')(c1)
    p1 = MaxPooling2D((2, 2))(c1)

    c2 = Conv2D(64, (3, 3), activation='relu', padding='same')(p1)
    c2 = Conv2D(64, (3, 3), activation='relu', padding='same')(c2)
    p2 = MaxPooling2D((2, 2))(c2)

    c3 = Conv2D(128, (3, 3), activation='relu', padding='same')(p2)
    c3 = Conv2D(128, (3, 3), activation='relu', padding='same')(c3)
    p3 = MaxPooling2D((2, 2))(c3)

    c4 = Conv2D(256, (3, 3), activation='relu', padding='same')(p3)
    c4 = Conv2D(256, (3, 3), activation='relu', padding='same')(c4)

    u5 = UpSampling2D((2, 2))(c4)
    u5 = Concatenate()([u5, c3])
    c5 = Conv2D(128, (3, 3), activation='relu', padding='same')(u5)
    c5 = Conv2D(128, (3, 3), activation='relu', padding='same')(c5)

    u6 = UpSampling2D((2, 2))(c5)
    u6 = Concatenate()([u6, c2])
    c6 = Conv2D(64, (3, 3), activation='relu', padding='same')(u6)
    c6 = Conv2D(64, (3, 3), activation='relu', padding='same')(c6)

    u7 = UpSampling2D((2, 2))(c6)
    u7 = Concatenate()([u7, c1])
    c7 = Conv2D(32, (3, 3), activation='relu', padding='same')(u7)
    c7 = Conv2D(32, (3, 3), activation='relu', padding='same')(c7)

    output = Conv2D(2, (3, 3), activation='tanh', padding='same')(c7)
    return Model(input_img, output)

model = build_unet_model()
model.compile(optimizer='adam', loss='mae')

checkpoint = ModelCheckpoint(CHECKPOINT_PATH, monitor='loss', verbose=1, save_best_only=True, mode='min')
history = model.fit(train_dataset, epochs=50, callbacks=[checkpoint])