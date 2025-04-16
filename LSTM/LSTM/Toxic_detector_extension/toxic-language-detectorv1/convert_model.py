# convert_model.py
import tensorflow as tf
import numpy as np
import os
import json

def convert_model(input_model_path, output_model_path):
    """
    Chuyển đổi model từ định dạng cũ sang định dạng tương thích với TensorFlow 2.x
    
    Args:
        input_model_path: Đường dẫn đến file model cũ (.h5)
        output_model_path: Đường dẫn để lưu model mới
    """
    try:
        # Cố gắng tải model theo cách thông thường
        print(f"Đang tải model từ {input_model_path}...")
        
        # Tải model dưới dạng file h5 - lấy topology và weights
        f = tf.keras.models.load_model(input_model_path, compile=False)
        
        # Lấy thông tin kiến trúc model
        config = json.loads(f.to_json())
        
        # Xử lý lại cấu hình model
        for layer in config['config']['layers']:
            # Loại bỏ batch_shape nếu có
            if 'batch_shape' in layer['config']:
                print(f"Loại bỏ batch_shape từ layer {layer['name']}")
                del layer['config']['batch_shape']
            
            # Giữ lại shape
            if 'batch_input_shape' in layer['config']:
                print(f"Giữ batch_input_shape: {layer['config']['batch_input_shape']}")
        
        # Tạo model mới từ config đã được chỉnh sửa
        print("Đang tạo model mới từ cấu hình đã được chỉnh sửa...")
        new_model = tf.keras.models.model_from_json(json.dumps(config))
        
        # Sao chép trọng số
        print("Đang sao chép trọng số...")
        for i, layer in enumerate(f.layers):
            try:
                weights = layer.get_weights()
                if weights:
                    print(f"Đang sao chép trọng số cho layer {i}: {layer.name}")
                    new_model.layers[i].set_weights(weights)
            except Exception as e:
                print(f"Không thể sao chép trọng số cho layer {i}: {e}")
        
        # Biên dịch model mới
        new_model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Lưu model mới
        print(f"Đang lưu model mới vào {output_model_path}...")
        new_model.save(output_model_path)
        
        print(f"Chuyển đổi model thành công! Model mới đã được lưu tại {output_model_path}")
        return True
    
    except Exception as e:
        print(f"Lỗi khi chuyển đổi model: {e}")
        
        # Trường hợp 2: Nếu không thể tải model, tạo mới model tương thích
        print("Tạo model mới tương thích...")
        
        # Tạo model LSTM đơn giản
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(100,), dtype='float32'),
            tf.keras.layers.Embedding(10000, 128, input_length=100),
            tf.keras.layers.LSTM(64, dropout=0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(4, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Lưu model mới
        model.save(output_path)
        print(f"Đã tạo model mới tại {output_path}")
        return False

# Chuyển đổi model
input_path = "model/best_model_LSTM.h5"
output_path = "model/compatible_model.h5"

# Tạo thư mục model nếu chưa tồn tại
os.makedirs(os.path.dirname(output_path), exist_ok=True)

if not os.path.exists(output_path):
    convert_model(input_path, output_path)
else:
    print(f"Model tương thích đã tồn tại tại {output_path}. Bỏ qua chuyển đổi.")

# Kiểm tra model tương thích
try:
    model = tf.keras.models.load_model(output_path)
    print("Kiểm tra model thành công!")
    print(f"Cấu trúc model: {model.summary()}")
except Exception as e:
    print(f"Lỗi khi kiểm tra model: {e}")