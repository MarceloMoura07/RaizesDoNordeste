class Config:
    SECRET_KEY = "supersecret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///raizes.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "jwt-secret"