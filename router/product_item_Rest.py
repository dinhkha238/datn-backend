from datetime import datetime
import json
import os
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from scipy.spatial.distance import cosine

from dbconnect import SessionLocal
from model.product_item import ProductItemBase
from service.product_item_DAO import add_product, delete_product, get_list_product_similar, monthly_revenue, product_item_by_id, product_items, save_image, statistic_product_item, update_product, user_spending_info

# Tải mô hình đã lưu
model = load_model("my_model.h5")

# Thư mục lưu tạm thời ảnh upload
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()

# Dependency để lấy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get-product-items", tags=["Product-Item"])
async def get_product_items(option: str, filter: str = None, sort: str = None, db = Depends(get_db)):
    items = product_items(option, filter, sort, db)
    return items

@router.get("/get-product-item/{id}", tags=["Product-Item"])
async def get_product_item(id: int, db = Depends(get_db)):
    item = product_item_by_id(id, db)
    return item

@router.get("/statistic-product-item", tags=["Product-Item"])
async def get_statistic_product_item(yy_mm:str = "", db = Depends(get_db)):
    list_product_item = statistic_product_item(db,yy_mm)
    return list_product_item

@router.get("/month-revenue", tags=["Product-Item"])
async def get_monthly_revenue(year:int = "", db = Depends(get_db)):
    list_monthly_revenue = monthly_revenue(db,year)
    return list_monthly_revenue

@router.get("/user-spending-info", tags=["Product-Item"])
async def get_user_spending_info(yy_mm:str = "",db = Depends(get_db)):
    list_user_spending_info = user_spending_info(db,yy_mm)
    return list_user_spending_info

@router.post("/add-product", tags=["Product-Item"])
async def post_add_product(
    product: str = Form(...), 
    file: UploadFile = File(...), 
    db = Depends(get_db)
):
    try:
        # Parse JSON product string thành dict
        product_data = json.loads(product)
        # Parse dict thành ProductItemBase
        product_obj = ProductItemBase(**product_data)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    
    # Save the uploaded file
    file_path = save_image(file)
    product_obj.url = file_path

    # Add product to DB
    add_product(product_obj, db)
    return {'message': 'Thêm sản phẩm thành công'}

@router.put("/update-product/{id}", tags=["Product-Item"])
async def put_update_product(
    id:int, 
    product: str = Form(...), 
    file: UploadFile = File(...), 
    db = Depends(get_db)
):
    try:
        # Parse JSON product string thành dict
        product_data = json.loads(product)
        # Parse dict thành ProductItemBase
        product_obj = ProductItemBase(**product_data)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    
    # Save the uploaded file
    file_path = save_image(file)
    product_obj.url = file_path

    update_product(id, product_obj, db)
    return {'message': 'Cập nhật sản phẩm thành công'}

@router.delete("/delete-product/{id}", tags=["Product-Item"])
async def delete_delete_product(id:int, db = Depends(get_db)):
    delete_product(id, db)
    return {'message': 'Xóa sản phẩm thành công'}

@router.post("/find-similar-images/")
async def find_similar(file: UploadFile = File(...),db = Depends(get_db)):
    try:
        # Lưu ảnh upload
        input_filename = os.path.join(UPLOAD_FOLDER, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        with open(input_filename, "wb") as f:
            content = await file.read()
            f.write(content)

        # Trích xuất đặc trưng của ảnh mới
        new_image_features = extract_features(input_filename, model)

        # Tải file NumPy
        database_features = np.load('images/Features/features.npy')
        list_of_image_paths = np.load('images/Features/image_paths.npy')

        # Tìm ảnh tương tự
        similarities = find_similar_images(new_image_features, database_features)
        if not similarities:
            return JSONResponse(content={"status": "error", "message": "Không tìm thấy ảnh tương tự."}, status_code=404)

        # Sắp xếp ảnh theo mức độ tương tự (từ nhỏ đến lớn)
        sorted_similarities = sorted(range(len(similarities)), key=lambda k: similarities[k])

        # Hiển thị top 5 ảnh tương tự
        top_similar_images = [list_of_image_paths[i] for i in sorted_similarities[:6]]

        updated_array = [item.replace("\\", "/") for item in top_similar_images]

        list_product_item = get_list_product_similar(updated_array,db)

        return list_product_item

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# Hàm tìm ảnh tương tự dựa trên khoảng cách cosin
def find_similar_images(features, database_features):
    similarities = []
    for db_feat in database_features:
        sim = cosine(features, db_feat)
        similarities.append(sim)
    return similarities

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

