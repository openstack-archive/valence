Horizon Valence plugin
=======================================

Horizon Valence plugin

##Install
1. Copy plugin files into your Horizon project

2. Register Valence Apis

3. Enable Debug (Optional)
    If you want to enable debug:
    (1). Set DEBUG = True in
        <OSDashBoardHome>/wsgi/django.wsgi
    (2). Set DEBUG = True in
        <OSDashBoardHome>/local/local_settings.py

4. Connection configuration
    DashBoardHome>local/local_settings.py,
    make sure these values are correct:
   ```
    OPENSTACK_KEYSTONE_URL = http://<authentication_IP>:5000/v2.0
    VALENCE_ADMIN_USER = {
        'username' : yourusername,
        'password' : yourpassword,
        'auth_url' : 'http://<authentication_IP>:5000/v2.0/',
        'tenant_name' : 'admin',
        'service_type' : 'baremetal',
        'endpoint_type' : 'public',
        'valence_url' : 'http://<valence_IP>:8181',
        'retry_interval':2
    }
    CONFLUENT_SETTING = {
        'ip' : 'Confluent_IP',
        'user' : 'testuser',
        'passwd' : 'Passw0rd',
    }
   ```
5. pre-execute
   ```
    cd <OSDashBoardHome>/../
    python manage.py collectstatic
    python manage.py compress
   ```
6. Restart Apache Service
   ```
    service httpd restart
   ```

