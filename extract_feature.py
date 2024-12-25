from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing import image
import glob
import os

# Tải mô hình đã lưu
model = load_model("my_model.h5")

# Trích xuất đặc trưng của một ảnh
def extract_features(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = img_data / 255.0

    features = model.predict(img_data)

    # Làm phẳng đầu ra
    features = features.flatten()
    return features

list_of_image_paths = []
folder_path = "images\San_pham"
list_of_image_paths = glob.glob(os.path.join(folder_path, '*.*'))  # Lấy tất cả file hình ảnh

print(list_of_image_paths)  # Hiển thị danh sách đường dẫn ảnh
database_features = []
for img_path in list_of_image_paths:
    feature = extract_features(img_path, model)
    database_features.append(feature)

# Lưu đặc trưng và đường dẫn ảnh
features_array = np.array(database_features)  # Chuyển danh sách đặc trưng thành mảng NumPy
image_paths_array = np.array(list_of_image_paths)  # Danh sách đường dẫn ảnh

# Lưu vào file
np.save('images\\Features\\features.npy', features_array)
np.save('images\\Features\\image_paths.npy', image_paths_array)

print("Đã lưu đặc trưng và đường dẫn ảnh vào file .npy")

# import numpy as np

# # Đọc file .npy
# data = np.load('images/Features/image_paths.npy')

# # In nội dung của mảng
# print(data)
