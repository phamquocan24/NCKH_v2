"""
Model Adapter - Lớp trung gian xử lý model safetensors
"""
import os
import tensorflow as tf
import logging

logger = logging.getLogger(__name__)

class ModelAdapter:
    """Adapter class để tải model từ định dạng .safetensors"""
    
    @staticmethod
    def load_model(model_path):
        """
        Tải model từ đường dẫn, tự động phát hiện định dạng
        
        Args:
            model_path: Đường dẫn đến file model
            
        Returns:
            tf.keras.Model: Model đã tải
        """
        if model_path.endswith('.safetensors'):
            return ModelAdapter._load_from_safetensors(model_path)
        else:
            # Mặc định cho .h5 và các định dạng khác
            return tf.keras.models.load_model(model_path)
    
    @staticmethod
    def _load_from_safetensors(model_path):
        """
        Tải model từ định dạng .safetensors
        
        Args:
            model_path: Đường dẫn đến file model .safetensors
            
        Returns:
            tf.keras.Model: Model đã tải
        """
        try:
            from safetensors.tensorflow import load_file
            
            # Tải weights từ file safetensors
            weights_dict = load_file(model_path)
            
            # Tạo model với kiến trúc tương tự model ban đầu
            model = ModelAdapter._create_compatible_model()
            
            # Áp dụng weights
            ModelAdapter._apply_weights(model, weights_dict)
            
            # Compile model
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model safetensors: {str(e)}")
            # Fallback về model .h5 nếu có
            h5_path = model_path.replace('.safetensors', '.h5')
            if os.path.exists(h5_path):
                logger.info(f"Fallback sang model .h5: {h5_path}")
                return tf.keras.models.load_model(h5_path)
            raise RuntimeError(f"Không thể tải model: {str(e)}")
    
    @staticmethod
    def _create_compatible_model():
        """
        Tạo model tương thích với kiến trúc của model ban đầu
        
        Returns:
            tf.keras.Model: Model tương thích
        """
        # Tạo model với kiến trúc giống model ban đầu
        inputs = tf.keras.Input(shape=(100,))
        x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128)(inputs)
        x = tf.keras.layers.LSTM(128)(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model
    
    @staticmethod
    def _apply_weights(model, weights_dict):
        """
        Áp dụng weights từ safetensors vào model TensorFlow
        
        Args:
            model: Model TensorFlow
            weights_dict: Dictionary chứa tensor weights
        """
        # Áp dụng weights cho từng layer
        for layer in model.layers:
            layer_name = layer.name
            weights = layer.get_weights()
            
            # Skip layer nếu không có weights
            if not weights:
                continue
                
            # Tìm tensor tương ứng cho mỗi weight
            new_weights = []
            for i, old_weight in enumerate(weights):
                # Thông thường, i=0 là kernel, i=1 là bias
                weight_type = "kernel" if i == 0 else "bias"
                
                # Các key name khả dĩ
                possible_keys = [
                    f"{layer_name}.{weight_type}",
                    f"{layer_name}/{weight_type}",
                    layer_name if i == 0 else f"{layer_name}_bias"
                ]
                
                # Tìm key trong weights_dict
                tensor_key = None
                for key in possible_keys:
                    if key in weights_dict:
                        tensor = weights_dict[key]
                        if tensor.shape == old_weight.shape:
                            new_weights.append(tensor)
                            break
                else:
                    # Nếu không tìm thấy, giữ nguyên weight cũ
                    new_weights.append(old_weight)
            
            # Áp dụng weights mới
            if len(new_weights) == len(weights):
                try:
                    layer.set_weights(new_weights)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")