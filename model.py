import numpy as np
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential


def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

def predict(model, input_vector):
    return model.predict(input_vector).argsort()

def build_model(weights):
    model = Sequential([
        # Dot product between feature vector and reference vectors
        Dense(input_shape=(13,),
              units=weights.shape[0],
              activation='linear',
              name='dense_1',
              use_bias=False)
    ])
    model.set_weights([weights.T])
    return model

def get_results(input_vector, features, best_match=True, amount=6):
    """
    get_results(input_vector, features, best_match=True,
                                        amount=6)

    input_vector: features of the song to suggest similar songs to

    features: features from full database to suggest songs from, plus track_ids

    best_match=True: True if you want most similar songs, False if least similar

    amount=6: amount of results to return.

    returns a list (might be a numpy array?) of indices from the original database
    """
    tr_id = input_vector['id'].values[0]
    ids = features['id']
    input_vec = input_vector.drop('id', axis=1)
    feats = features.drop('id', axis=1)
    norm_vector = normalize(input_vec.values.reshape(1,13))
    norm_features = normalize(feats)
    model = build_model(norm_features)
    prediction = np.array(predict(model, norm_vector).argsort())
    prediction = prediction.reshape(prediction.shape[1])
    if best_match:
        if tr_id in ids[prediction[-amount:]]:
            return features.loc[prediction[-amount-1:-1]]
        return features.loc[prediction[-amount:]]
    return features.loc[prediction[:amount]]
