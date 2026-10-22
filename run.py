from app import create_app

app = create_app()

if __name__ == "__main__":
    # Keep local demo startup deterministic even if a parent shell exports
    # FLASK_DEBUG=1. The reloader can spawn a second process and the interactive
    # debugger must not be exposed by the default run command.
    app.run(debug=False, use_reloader=False)
