# route.py

from datetime import datetime
import os
import json
import pprint
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    jsonify,
    current_app,
    Response,
    abort,
    send_from_directory
)
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
from guess_language import guess_language
from app import db, logging
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, EditTermForm, EditNodeForm, DeprecateTermForm, DiffForm
import app.search
from app.models import User, Post, Entity
from app.main import bp
from app.util import get_yaml_for
import app.mdb
from app.arc import get_diff


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

        if format == 'yaml':
            yaml = get_yaml_for(model_.handle)
            return Response(yaml, mimetype='text/plain')

        else:
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


@bp.route("/nodes/<id>", methods=['GET', 'POST'])
@bp.route("/nodes")
@login_required
def nodes(id=None):

    format = request.args.get("format")
    model = request.args.get("model")

    m = app.mdb.mdb()

    # A: single node
    if id is not None:
        node_ = m.get_node_by_id(id)
        # FIXME check that id actually exists - handle error

        form = EditNodeForm()
        if form.validate_on_submit():
            m.update_node_by_id(id, form.nodeHandle.data)
            flash(_("Your changes have been saved."))
            return redirect(url_for("main.nodes", id=id))

        elif request.method == "GET":
            form.nodeHandle.data = node_['handle']

            if format == "json":
                return jsonify(node_)
            else:
                return render_template(
                    "mdb-node.html",
                    title=_("Node"),
                    mdb=node_,
                    subtype="main.nodes",
                    display="detail",
                    form=form,
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

        editform = EditTermForm()
        deprecateform = DeprecateTermForm()
        
        if editform.validate_on_submit():
            # go and make actual changes ...
            m.update_term_by_id(id, editform.termvalue.data)
            flash(_("Your changes have been saved."))
            return redirect(url_for("main.terms", id=id))

        elif deprecateform.validate_on_submit():
            m.deprecate_term(id)
            flash(_("Term has been deprecated."))
            return redirect(url_for("main.terms"))           

        if request.method == "GET":
            editform.termvalue.data = term_['value']

            if format == "json":
                return jsonify(term_)
            else:
                return render_template(
                    "mdb-term.html",
                    title=_("Term"),
                    mdb=term_,
                    subtype="main.terms",
                    display="detail",
                    form=editform,
                    deprecateform=deprecateform,
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


@bp.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@bp.route("/diff", methods=['GET', 'POST'])
@login_required
def diff():
    '''stub for yaml diff functionality'''
    current_app.logger.warn('>>>now in diff')
    # simple check of app.config
    file_choices = [('', '')]
    APP_ROOT = os.path.dirname(os.path.abspath(current_app.root_path))   # refers to application_top
    APP_UPLOAD_PATH = os.path.join(APP_ROOT, current_app.config['UPLOAD_PATH'])
    files = os.listdir(APP_UPLOAD_PATH)
    current_app.logger.warn('the APP_ROOT is at: {}'.format(APP_ROOT))
    current_app.logger.warn('the uploads dir is at: {}'.format(APP_UPLOAD_PATH))
    current_app.logger.warn('the uploads dir has: {}'.format(files))
    current_app.logger.warn('the uploads dir is {}'.format(current_app.config['UPLOAD_PATH']))

    for _file in files:
        current_app.logger.warn('... Adding a new file')
        tup = (_file, _file)
        file_choices.append(tup)

    current_app.logger.warn('the options for file_choices is {}'.format(file_choices))

    dform = DiffForm()
    dform.mdf_a.choices = file_choices
    dform.mdf_b.choices = file_choices

    mdf_diff = ''
    if dform.validate_on_submit():
        current_app.logger.info('  CLICK !!!! ')

        mdf_a = dform.mdf_a.data
        mdf_b = dform.mdf_b.data

        if (mdf_a and mdf_b):
            # simple bento_meta/diff poc using stub/test yaml
            _diff = app.arc.diff_mdf(mdf_a, mdf_b)
            mdf_diff = pprint.pformat(_diff)
            current_app.logger.info('Lastly diff output is {}'.format(mdf_diff))
    
    elif (request.method == 'POST'):
        current_app.logger.warn(' >>> now is INTERNAL ')

        uploaded_file = request.files.get('file')

        if (uploaded_file):
            filename = secure_filename(uploaded_file.filename)
            current_app.logger.info(' >>> upload_files() has filename {}'.format(filename))

            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                    return "Invalid yaml", 400

                APP_ROOT = os.path.dirname(os.path.abspath(current_app.root_path))   # refers to application_top
                APP_UPLOAD_PATH = os.path.join(APP_ROOT, current_app.config['UPLOAD_PATH'])
                uploaded_file.save(os.path.join(APP_UPLOAD_PATH, filename))
                current_app.logger.info(' >>> upload_files() -- save')

    # return deltapp, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return render_template('diff.html', form=dform, mdf_diff=mdf_diff)


@bp.route("/upload_files", methods=['POST'])
@login_required
def upload_files():
    current_app.logger.warn(' > now is upload_files()')

    uploaded_file = request.files.get('file')

    if (uploaded_file):
        filename = secure_filename(uploaded_file.filename)
        current_app.logger.info(' > upload_files() has filename {}'.format(filename))

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                return "Invalid yaml", 400

            APP_ROOT = os.path.dirname(os.path.abspath(current_app.root_path))   # refers to application_top
            APP_UPLOAD_PATH = os.path.join(APP_ROOT, current_app.config['UPLOAD_PATH'])
            uploaded_file.save(os.path.join(APP_UPLOAD_PATH, filename))
            current_app.logger.info(' > upload_files() -- save')
    return redirect(url_for('main.diff'))

@bp.route('/uploads/<filename>')
def upload(filename):
    current_app.logger.warn('>>>now in upload')
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)