import os
from keras.models import Model
from keras.layers import Input
import cv2
import numpy as np
from keras import backend as K
import pickle
from timeit import default_timer as timer
from dobble.network import nn_base, rpn_layer, classifier_layer, RoiPoolingConv
from dobble.utilities import Config, format_img, non_max_suppression_fast, rpn_to_roi

# Building Model and Loading Weights

num_features = 512

base_path = '.'
model_path = os.path.join(base_path, 'model/model_frcnn_vgg.hdf5')
config_output_filename = os.path.join(base_path, 'model_vgg_config.pickle')
with open(config_output_filename, 'rb') as f_in:
    C = pickle.load(f_in)

# Input
input_shape_img = (None, None, 3)
input_shape_features = (None, None, num_features)
img_input = Input(shape=input_shape_img)
roi_input = Input(shape=(C.num_rois, 4))
feature_map_input = Input(shape=input_shape_features)

# Output
num_anchors = len(C.anchor_box_scales) * len(C.anchor_box_ratios)
shared_layers = nn_base(img_input, trainable=True)
rpn_layers = rpn_layer(shared_layers, num_anchors)
classifier = classifier_layer(
    feature_map_input, roi_input, C.num_rois, nb_classes=len(C.class_mapping))

# Model
model_rpn = Model(img_input, rpn_layers)
model_classifier_only = Model([feature_map_input, roi_input], classifier)
model_classifier = Model([feature_map_input, roi_input], classifier)

# Weights
print('Loading weights from {}'.format(model_path))
model_rpn.load_weights(model_path, by_name=True)
model_classifier.load_weights(model_path, by_name=True)

# Compile
model_rpn.compile(optimizer='sgd', loss='mse')
model_classifier.compile(optimizer='sgd', loss='mse')


def predict(img_path):
    # Prediction
    # Config
    # img_path = base_path + '/custom_pics/IMG_3507.jpg'
    bbox_threshold = 0.7
    class_mapping = C.class_mapping
    class_mapping = {v: k for k, v in class_mapping.items()}

    # Show Img
    img = cv2.imread(img_path)

    # Predict
    X, ratio = format_img(img, C)

    X = np.transpose(X, (0, 2, 3, 1))

    start = timer()
    [Y1, Y2, F] = model_rpn.predict(X)
    end = timer()
    print("Time spent model_rpn predict:", end - start)

    R = rpn_to_roi(Y1, Y2, C, K.image_dim_ordering(), overlap_thresh=0.7)
    # convert from (x1,y1,x2,y2) to (x,y,w,h)
    R[:, 2] -= R[:, 0]
    R[:, 3] -= R[:, 1]

    bboxes = {}
    probs = {}
    for jk in range(R.shape[0] // C.num_rois + 1):
        ROIs = np.expand_dims(
            R[C.num_rois * jk:C.num_rois * (jk + 1), :], axis=0)
        if ROIs.shape[1] == 0:
            break

        if jk == R.shape[0] // C.num_rois:
            # pad R
            curr_shape = ROIs.shape
            target_shape = (curr_shape[0], C.num_rois, curr_shape[2])
            ROIs_padded = np.zeros(target_shape).astype(ROIs.dtype)
            ROIs_padded[:, :curr_shape[1], :] = ROIs
            ROIs_padded[0, curr_shape[1]:, :] = ROIs[0, 0, :]
            ROIs = ROIs_padded

        start = timer()
        [P_cls, P_regr] = model_classifier_only.predict([F, ROIs])
        end = timer()
        print("Time spent model_classifier predict:", end - start)

        for ii in range(P_cls.shape[1]):
            # Ignore 'bg' class
            if np.max(P_cls[0, ii, :]) < bbox_threshold or np.argmax(P_cls[0, ii, :]) == (P_cls.shape[2] - 1):
                continue

            cls_name = class_mapping[np.argmax(P_cls[0, ii, :])]

            if cls_name not in probs:
                probs[cls_name] = []
                bboxes[cls_name] = []

            (x, y, w, h) = ROIs[0, ii, :]

            cls_num = np.argmax(P_cls[0, ii, :])
            try:
                (tx, ty, tw, th) = P_regr[0, ii, 4 * cls_num:4 * (cls_num + 1)]
                tx /= C.classifier_regr_std[0]
                ty /= C.classifier_regr_std[1]
                tw /= C.classifier_regr_std[2]
                th /= C.classifier_regr_std[3]
                x, y, w, h = apply_regr(x, y, w, h, tx, ty, tw, th)
            except:
                pass
            bboxes[cls_name].append([C.rpn_stride * x, C.rpn_stride * y,
                                     C.rpn_stride * (x + w), C.rpn_stride * (y + h)])
            probs[cls_name].append(np.max(P_cls[0, ii, :]))

    all_dets = []
    for key in bboxes:
        bbox = np.array(bboxes[key])

        new_boxes, new_probs = non_max_suppression_fast(
            bbox, np.array(probs[key]), overlap_thresh=0.2)
        for jk in range(new_boxes.shape[0]):
            (x1, y1, x2, y2) = new_boxes[jk, :]

            all_dets.append((key, 100 * new_probs[jk]))

    return all_dets


print("Model ready")

start = timer()
result = predict(img_path=base_path + '/custom_pics/IMG_3430.jpg')
print(result)
end = timer()
print("Time spent:", end - start)

start = timer()
result = predict(img_path=base_path + '/custom_pics/IMG_3430.jpg')
print(result)
end = timer()
print("Time spent:", end - start)
