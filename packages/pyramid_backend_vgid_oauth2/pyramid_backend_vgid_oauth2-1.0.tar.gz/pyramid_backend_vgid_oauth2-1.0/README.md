pyramid_backend_vgid_oauth2
===========================

Hệ thống quản trị người dùng backend mặc định dành cho pyramid_backend dựa trên pyramid_vgid_oauth2

Sử dụng
-------

    # cần inlcude "pyramid_backend", "pyramid_vgid_oauth2" cùng configuration trước đó
    config.include('pyramid_backend_vgid_oauth2')
    config.set_authorization_policy(...)

### Configuration

    pyramid_backend_vgid_oauth2.auth_secret = option, key để mã hóa cookie đăng nhập

Hệ thống này sử dụng backend để lưu trữ User dựa trên SQLAlchemy, chỉ cần config biến DBSession
là được

    pyramid_backend_vgid_oauth2.sa.dbsession = 'đường dẫn đến dbsession'


CHANGE LOG
----------

### 1.0.x

* Packaging