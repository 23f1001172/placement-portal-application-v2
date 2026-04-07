class Config:
    SECRET_KEY = 'secret123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Run the test server with: python -m smtpd -n -c DebuggingServer localhost:1025
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'placementportal@localhost'
    ADMIN_EMAIL = 'admin@localhost'   # The admin email address for monthly reports