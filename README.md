Login:

- B1: Vào trang http://127.0.0.1:8000/admin/ đăng nhập bằng tài khoản admin
- B2: Vào trang http://127.0.0.1:8000/api/v1/o/applications/ tạo 1 application mới để lấy client_id và client_secret (LƯU Ý: Để client_type=confidential,
  authorization_grant_type=password, client_id và client_secret phải lưu lại trước khi ấn SAVE). Cái này chỉ cần tạo 1 LẦN DUY NHẤT, chỉ tạo lại khi DROP
  DATABASE và MIGRATE lại
- B3: Lên Postman qua GLOBAL environment thay đổi client_id và client_secret vừa lấy ở B2 để test API

Register: Đã để sẵn description cho từng trường ở Postman

Current User: Login xong thì lấy access_token xong qua GLOBAL environment thay đổi AUTHORIZATION để test API

Update Current User: Login xong thì lấy access_token xong qua GLOBAL environment thay đổi AUTHORIZATION để test API, đã để sẵn description cho từng trường ở
Postman