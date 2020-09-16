# route.py

from datetime import datetime
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    jsonify,
    current_app,
)
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, EditTermForm
import app.search
from app.models import User, Post, Entity
from app.translate import translate
from app.main import bp
import app.mdb


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == "UNKNOWN" or len(language) > 5:
            language = ""
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_("Your post is now live!"))
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = url_for("main.index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.index", page=posts.prev_num) if posts.has_prev else None
    return render_template(
        "index.html",
        title=_("Home"),
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@bp.route("/models/<name>")
@bp.route("/models")
@login_required
def models(name=None):
    format = request.args.get("format")
    m = app.mdb.mdb()

    if name is not None:
        model_ = m.get_model_by_name(name)
        return render_template(
            "mdb-model.html",
            title=_("Model: {}".format(model_.handle)),
            mdb=model_,
            subtype="main.models",
            display="detail",
    )

    else:
        models_ = m.get_list_of_models()
        return render_template(
            "mdb-model.html",
            title=_("Models"),
            mdb=models_,
            subtype="main.models",
            display="list",
    )


@bp.route("/nodes/<id>")
@bp.route("/nodes")
@login_required
def nodes(id=None):

    format = request.args.get("format")
    model = request.args.get("model")

    m = app.mdb.mdb()

    # A: single node
    if id is not None:
        node_ = m.get_node_by_id(id)
        # TODO check that id actually exists - handle error

        if format == "json":
            return jsonify(node_)
        else:
            return render_template(
                "mdb-node.html",
                title=_("Node"),
                mdb=node_,
                subtype="main.nodes",
                display="detail",
            )

    # B: filter by model
    if model is not None:
        # TODO check that id actually exists - handle error
        nodes_ = m.get_list_of_nodes(model)

        if format == "json":
            return jsonify(nodes_)
        else: 
            return render_template(
                "mdb-node-list.html",
                title=_("Nodes in Model {}".format(model)),
                mdb=nodes_,
                subtype="main.nodes",
                display="list-by-model",
            )

    # C: plain list
    nodes_ = m.get_list_of_nodes()
    if format == "json":
        return jsonify(nodes_)
    else:
        return render_template(
            "mdb.html",
            title=_("Nodes"),
            mdb=nodes_,
            subtype="main.nodes",
            display="list",
        )


@bp.route("/valuesets/<id>")
@bp.route("/valuesets")
@login_required
def valuesets(id=None):

    format = request.args.get("format")
    model = request.args.get("model")
    print("ya, got model".format(model))
    m = app.mdb.mdb()

    if id is not None:
        vs_ = m.get_valueset_by_id(id, model)

        if vs_ is None or not bool(vs_):
            return render_template('/errors/400.html'), 400

        # TODO check that id actually exists - handle error
        if format == "json":
            return jsonify(vs_)
        else:
            return render_template(
                "mdb-valueset.html",
                title=_("Value Set: "),
                mdb=vs_,
                subtype="main.valuesets",
                display="detail",
            )

    else:
        vs_ = m.get_list_of_valuesets(model)
        if format == "json":
            return jsonify(vs_)
        else:
            return render_template(
                "mdb.html",
                title=_("Value Sets"),
                mdb=vs_,
                subtype="main.valuesets",
                display="list",
            )


@bp.route("/terms/<id>", methods=['GET', 'POST'])
@bp.route("/terms")
@login_required
def terms(id=None):

    format = request.args.get("format")
    m = app.mdb.mdb()

    if id is not None:
        term_ = m.get_term_by_id(id)

        form = EditTermForm()
        if form.validate_on_submit():
            # would actually make chages here
            # current_user.username = form.username.data
            #current_user.about_me = form.about_me.data
            #db.session.commit()
            flash(_("Your changes have been saved."))
            return redirect(url_for("main.terms"))  ## ?? 

        elif request.method == "GET":
            form.termname.data = term_['value']

            if format == "json":
                return jsonify(term_)
            else:
                return render_template(
                    "mdb-term.html",
                    title=_("Term"),
                    mdb=term_,
                    subtype="main.terms",
                    display="detail",
                    form=form,
                )
    else:
        terms_ = m.get_list_of_terms()
        if format == "json":
            return jsonify(terms_)
        else:
            return render_template(
                "mdb.html",
                title=_("Terms"),
                mdb=terms_,
                subtype="main.terms",
                display="list",
            )


@bp.route("/origins/<id>")
@bp.route("/origins")
@login_required
def origins(id=None):
    format = request.args.get("format")
    m = app.mdb.mdb()

    origins_ = m.get_list_of_origins()
    if format == "json":
        return jsonify(origins_)

    return render_template(
        "mdb.html",
        title=_("Origins"),
        mdb=origins_,
        subtype="main.origins",
        display="list",
    )


# ---------------------------------------------------------------------------
@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.user", username=user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title=_("Edit Profile"), form=form)


@bp.route("/search")
@login_required
def search():

    if not g.search_form.validate():
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)

    hits, total = Entity.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )
    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )
    return render_template(
        "search.html",
        title=_("Search"),
        hits=hits,
        next_url=next_url,
        prev_url=prev_url,
    )

@bp.route("/about-mdb")
@login_required
def about_mdb():
    return render_template("about-mdb.html", title=_("About MDB"))


@bp.route("/about-sts")
@login_required
def about_sts():
    return render_template("about-sts.html", title=_("About STS"))

