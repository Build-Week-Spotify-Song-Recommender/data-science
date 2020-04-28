class KNN_Model:
    def normalize(vectors):
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def predict(model, input_vector):
        return model.predict(input_vector.reshape(1,13)).argsort()

    def build_model(weights):
        model = Sequential([
            # Dot product between feature vector and reference vectors
            Dense(input_shape=(13,),
                  units=features.shape[0],
                  activation='linear',
                  name='dense_1',
                  use_bias=False)
        ])
        model.set_weights([weights.T])
        return model

    def get_results(input_vector, features, best_match=True, input_id=None, track_ids=None, amount=6):
        """
        get_results(input_vector, features, best_match=True,
                                            input_id=None,
                                            track_ids=None,
                                            amount=6)

        input_vector: features of the song to suggest similar songs to

        features: features from full database to suggest songs from

        best_match=True: True if you want most similar songs, False if least similar

        input_id=None: use in conjunction with track_ids to prevent returning input song;
            only relevant when best_match=True

        track_ids=None: track_ids from full database to suggest songs from;
            use this if you want to prevent returning suggestion of input song;
            only relevant when best_match=True and input_id != None

        amount=6: amount of results to return.

        returns a list (might be a numpy array?) of indices from the original database
        """

        norm_vector = self.normalize(input_vector)
        norm_features = self.normalize(features)
        model = self.build_model(norm_features)
        prediction = self.predict(model, norm_vector).argsort()
        if best_match:
            if track_ids is None:
                return prediction[-amount:]
            if track_id is None:
                return prediction[-amount:]
            if track_id in track_ids[prediction[-amount:]]:
                return prediction[-amount-1:1]
            return prediction[-amount:0]
        return prediction[:amount]
