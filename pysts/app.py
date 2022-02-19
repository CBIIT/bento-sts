from app import create_app, cli
# from app.models import User, Post

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    pass
#    return {"db": db}
#    return {"db": db, "User": User, "Post": Post}
