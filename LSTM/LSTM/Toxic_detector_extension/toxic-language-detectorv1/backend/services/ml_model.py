# services/ml_model.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import os

class MLModel:
    def __init__(self, model_path="model/best_model_LSTM.h5", max_length=100, max_words=20000):
        self.model_path = model_path
        self.max_length = max_length
        self.max_words = max_words
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the pretrained model trained on Vietnamese social media data"""
        try:
            if os.path.exists(self.model_path):
                # Cố gắng tải mô hình bình thường
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"Vietnamese toxicity model loaded from {self.model_path}")
            else:
                print(f"Model not found at {self.model_path}. Using dummy model.")
                self.model = self._create_dummy_model()
        except TypeError as e:
            if "Unrecognized keyword arguments: ['batch_shape']" in str(e):
                print("Detected compatibility issue with the model. Using custom loader...")
                # Tùy chỉnh tải mô hình để xử lý lỗi tương thích
                try:
                    # Tải mô hình với custom_objects
                    self.model = tf.keras.models.load_model(self.model_path, compile=False, 
                                                            custom_objects={'InputLayer': self._fix_input_layer})
                    print("Model loaded successfully with custom loader")
                except Exception as custom_e:
                    print(f"Custom loader failed: {custom_e}. Using dummy model.")
                    self.model = self._create_dummy_model()
            else:
                print(f"Unknown error loading model: {e}. Using dummy model.")
                self.model = self._create_dummy_model()
        except Exception as e:
            print(f"Error loading model: {e}. Using dummy model.")
            self.model = self._create_dummy_model()
        
        # In production, this should be loaded from a saved tokenizer trained on Vietnamese data
        # For Vietnamese text, we need a specialized tokenizer or use a pre-tokenized approach
        try:
            tokenizer_path = "model/vietnamese_tokenizer.pkl"
            if os.path.exists(tokenizer_path):
                import pickle
                with open(tokenizer_path, 'rb') as handle:
                    self.tokenizer = pickle.load(handle)
                print(f"Vietnamese tokenizer loaded from {tokenizer_path}")
            else:
                print("Tokenizer not found, initializing new one (for development only)")
                self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
    
    def _fix_input_layer(self, config):
        """Fix compatibility issues with older InputLayer configurations"""
        if 'batch_shape' in config:
            batch_shape = config.pop('batch_shape')
            config['batch_input_shape'] = batch_shape
        return tf.keras.layers.InputLayer(**config)
    
    def _create_dummy_model(self):
        """Create a dummy model for testing purposes"""
        inputs = tf.keras.Input(shape=(self.max_length,))
        x = tf.keras.layers.Embedding(self.max_words, 128, input_length=self.max_length)(inputs)
        x = tf.keras.layers.LSTM(128)(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_text(self, text):
        """Preprocess Vietnamese text for prediction"""
        # For Vietnamese, we need to maintain special characters and diacritical marks
        # Only remove punctuation and normalize whitespace
        text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Use underthesea for Vietnamese tokenization if available
        try:
            from underthesea import word_tokenize
            tokenized_text = word_tokenize(text, format="text")
            text = tokenized_text
        except ImportError:
            # Fallback if underthesea is not available
            pass
        
        # Tokenize and pad
        sequences = self.tokenizer.texts_to_sequences([text])
        padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        
        return padded_sequences
    
    def predict(self, text):
        """Predict the class of the Vietnamese text"""
        # Preprocess text
        preprocessed_text = self.preprocess_text(text)
        
        # Make prediction
        prediction = self.model.predict(preprocessed_text)[0]
        
        # Get class and confidence
        predicted_class = np.argmax(prediction)
        confidence = float(prediction[predicted_class])
        
        # Map prediction to labels appropriate for Vietnamese content
        # 0: clean, 1: offensive, 2: hate, 3: spam
        return int(predicted_class), confidence