def register_blueprints(app):
    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.groups import groups_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(admin_bp)
