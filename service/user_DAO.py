# from database import Database
from database import create_connection
from model.customer import Customer
from model.employee import Employee
from model.user import User
from sqlalchemy.orm import Session

def all_users(db:Session):
    # Lấy tất cả các User từ cơ sở dữ liệu
    users = db.query(User).all()
    
    # Danh sách kết quả
    user_with_roles = []
    
    for user in users:
        # Tạo từ điển chứa các thuộc tính của User
        user_dict = user.__dict__.copy()
        user_dict.pop("_sa_instance_state", None)  # Loại bỏ thuộc tính nội bộ của SQLAlchemy
        
        # Kiểm tra xem User có trong bảng Customer không
        customer = db.query(Customer).filter(Customer.userId == user.id).first()
        if customer:
            user_dict["role"] = "kh"  # Nếu là Customer, role = "kh"
        else:
            # Nếu không là Customer, kiểm tra trong bảng Employee
            employee = db.query(Employee).filter(Employee.userId == user.id).first()
            if employee:
                # Thêm role từ Employee và các thuộc tính (trừ id)
                user_dict["role"] = employee.role
                employee_dict = employee.__dict__.copy()
                employee_dict.pop("id", None)  # Loại bỏ `id`
                employee_dict.pop("_sa_instance_state", None)  # Loại bỏ thuộc tính nội bộ
                user_dict.update(employee_dict)  # Kết hợp các thuộc tính từ Employee vào User
        
        # Đưa vào danh sách kết quả
        user_with_roles.append(user_dict)
    
    return user_with_roles
    
def check_customer(username, password, db:Session):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        customer = db.query(Customer).filter(Customer.userId == user.id).first()
        if customer:
            return customer
    return None

def check_employee(username, password, db:Session):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        employee = db.query(Employee).filter(Employee.userId == user.id).first()
        if employee:
            employee.user = user
            return employee
    return None

def existing_customer(username, db:Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    return user

def info_customer(id, db:Session):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if customer:
        user = db.query(User).filter(User.id == customer.userId).first()
        return user
    return None
    
def create_user(fullname, username, password, contact, address, gender, birth, role_user, db:Session):
    user = User(fullname=fullname, username=username, password=password, contact=contact, address=address, gender=gender, birth=birth)
    db.add(user)
    db.commit()
    user = existing_customer(username, db)
    if(role_user == "kh"):
        customer = Customer(userId=user.id)
        db.add(customer)
    else:
        employee = Employee(userId=user.id, role = role_user)
        db.add(employee)
    db.commit()
    return user

def update_user(id, body, db:Session):
    user = db.query(User).filter(User.id == id).first()
    if user:
        if(body['role'] and body['role']!="kh" ):
            employee = db.query(Employee).filter(Employee.userId == user.id).first()
            employee.role = body['role']
        user.fullname = body['fullname']
        user.address = body['address']
        user.contact = body['contact']
        user.password = body['password']
        user.gender = body['gender']
        # dùng db.commit() để lưu thay đổi vào database
        db.commit()
        return user
    return None

def delete_user(id, role_user, db:Session):
    user = db.query(User).filter(User.id == id).first()
    if user:
        db.delete(user)
        if(role_user == "kh"):
            customer = db.query(Customer).filter(Customer.userId == user.id).first()
            db.delete(customer)
        else:
            employee = db.query(Employee).filter(Employee.userId == user.id).first()
            db.delete(employee)
        db.commit()
        return
    return None


            