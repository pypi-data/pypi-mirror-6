Pyramid VGID OAuth2
=============================================

Thư viện cho phép pyramid login thông qua https://id.vatgia.com một cách nhanh
chóng

Usage
---------------

Để sử dụng, thêm dòng sau đây vào hàm main(...):

    config.include("pyramid_vgid_oauth2")

Trong *development.ini*

    pyramid_vgid_oauth2.client_id = {Client ID cấp bởi VGID}
    pyramid_vgid_oauth2.client_secret = {Client Secret cấp bởi VGID}
    pyramid_vgid_oauth2.put_user_callback = Đường dẫn đến hàm sẽ được gọi để tạo mới User
    pyramid_vgid_oauth2.base_url = /vgid/oauth (đường dẫn dùng để login trên web hiện tại)

### Callback để tạo mới User

    def put_user_callback(acc):
        """
        :type acc: dict
        :return object phai co 1 field la .id
        """
        pass

### API

    request.vgid_access_token

có thể dùng để lấy access_token khi đã đăng nhập

#### Event

1. pyramid_vgid_oauth2.events.SignIn
2. pyramid_vgid_oauth2.events.SignOut