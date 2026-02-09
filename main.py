from flask import Flask, request, session, redirect, url_for, render_template, jsonify, flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from extensions import bcrypt
from datetime import datetime
import time
from functools import wraps
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from database.model.base import db
from database.model.groupModel import GroupModel, save_group, delete_group
from database.model.groupMemberModel import GroupMemberModel
from database.model.accountModel import AccountModel
from services.accountService import service_create_account, service_login_user
from database.model.groupActionModel import GroupActionModel

from utils.profanity import validate_text_fields
from utils.profanity import contains_profanity
from utils.profanity_config import GROUP_TEXT_FIELDS
# @todo: suche anpassen. Wenn nichts gefunden angezeigter text usw bei beiden abschnitten. Oben wegmachen du bist in keiner gruppe sondern nix gefunden
# @todo: und unten weg machen es sind keine offenen Gruppen dies das. Und wenn was gefunden, dann weg machen "keine Gruppen gefunden für X"

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("account_id") is None:
            flash("Bitte zuerst einloggen.", "danger")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("account_id") is None:
            flash("Bitte zuerst einloggen.", "danger")
            return redirect(url_for("login"))

        acc = db.session.get(AccountModel, session["account_id"])
        if not acc or acc.role != "ADMIN":
            flash("Keine Berechtigung.", "danger")
            return redirect(url_for("index"))

        return view(*args, **kwargs)
    return wrapped


def require_membership(group_id: int):
    account_id = session.get("account_id")
    membership = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id,
        accepted=True
    ).first()
    return membership is not None


ALLOWED_GRADES = {"Unterstufe", "Mittelstufe", "Oberstufe"}
MAX_GROUP_MEMBERS = 20


app = Flask(__name__)
bcrypt.init_app(app)
app.config["SECRET_KEY"] = "dlajwasdhdddqwf98fg9f23803f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

db.init_app(app)
with app.app_context():
    db.create_all()


# CSRF Fehler
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("Sicherheitscheck fehlgeschlagen (CSRF). Bitte Seite neu laden und erneut versuchen.", "danger")
    return redirect(url_for("index"))


@app.template_filter("dt_local")
def dt_local(unix_ts):
    """Unix timestamp (seconds) -> 'DD.MM.YYYY · HH:MM'"""
    if not unix_ts:
        return ""
    try:
        dt = datetime.fromtimestamp(int(unix_ts))
        return dt.strftime("%d.%m.%Y · %H:%M")
    except Exception:
        return ""


@app.route("/", methods=['GET'])
def index():
    if session.get("account_id"):
        account_id = session.get("account_id")
        search = (request.args.get("q") or "").strip()

        query = GroupModel.query.filter_by(is_active=True)

        if search:
            from sqlalchemy import or_
            like = f"%{search}%"
            query = query.filter(
                or_(
                    GroupModel.subject.ilike(like),
                    GroupModel.topic.ilike(like),
                )
            )

        groups = query.order_by(GroupModel.appointment.desc()).all()

        my_groups = []
        if account_id:
            query_my = (
                GroupModel.query
                .join(GroupMemberModel, GroupMemberModel.group_id == GroupModel.id)
                .filter(
                    GroupModel.is_active == True,
                    GroupMemberModel.account_id == account_id,
                    GroupMemberModel.accepted == True
                )
            )

            if search:
                from sqlalchemy import or_
                like = f"%{search}%"
                query_my = query_my.filter(or_(
                    GroupModel.subject.ilike(like),
                    GroupModel.topic.ilike(like),
                ))

            my_groups = query_my.order_by(GroupModel.created.desc()).all()

        now = int(time.time())
        today = datetime.now().date()

        my_ids = {g.id for g in my_groups}
        groups = [g for g in groups if g.id not in my_ids]

        groups_for_meta = {g.id: g for g in (groups + my_groups)}.values()
        group_meta = {}

        for g in groups_for_meta:
            status = None

            member_count = GroupMemberModel.query.filter_by(group_id=g.id).count()
            is_full = member_count >= MAX_GROUP_MEMBERS

            if g.appointment:
                ts = int(g.appointment)
                dt = datetime.fromtimestamp(ts)

                if ts < now:
                    status = "past"
                elif dt.date() == today:
                    status = "today"
                else:
                    status = "future"

            group_meta[g.id] = {
                "status": status,
                "member_count": member_count,
                "group_limit": MAX_GROUP_MEMBERS,
                "is_full": is_full,
            }

        return render_template(
            "index.html",
            account_id=account_id,
            my_groups=my_groups,
            groups=groups,
            group_meta=group_meta,
            search=search,
        )
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@app.route("/login_user", methods=["POST"])
def login_user():
    ok, errors = service_login_user(request.form)

    for e in errors:
        flash(e, "danger")

    if ok:
        flash("Erfolgreich eingeloggt.", "success")
        return redirect(url_for("index"))

    return redirect(url_for("login"))


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("account_id", None)
    flash("Du wurdest ausgeloggt.", "info")
    return redirect(url_for("index"))


@app.route("/register_account", methods=['GET'])
def register_account():
    return render_template('register.html')


@app.route("/create_account", methods=["POST"])
def create_account():
    ok, errors = service_create_account(request.form)

    for e in errors:
        flash(e, "danger")

    if ok:
        flash("Account erstellt. Bitte einloggen.", "success")
        return redirect(url_for("login"))

    return redirect(url_for("register_account"))


@app.route("/groups/<int:group_id>", methods=["GET"])
@login_required
def group_overview(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    if not require_membership(group_id):
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for("index"))

    member_count = GroupMemberModel.query.filter_by(group_id=group.id).count()
    owner_account = db.session.get(AccountModel, group.owner)
    owner_first_name = owner_account.first_name.strip() if owner_account and owner_account.first_name else "Unbekannt"
    grade = group.grade

    now = int(time.time())
    appointment_is_past = bool(group.appointment and int(group.appointment) < now)

    messages = (
        GroupActionModel.query
        .options(joinedload(GroupActionModel.account))
        .filter_by(group_id=group_id, type="MESSAGE")
        .order_by(GroupActionModel.created.asc())
        .all()
    )

    current_user_id = session.get("account_id")

    return render_template(
        "group_overview.html",
        group=group,
        member_count=member_count,
        group_limit=MAX_GROUP_MEMBERS,
        owner_first_name=owner_first_name,
        grade=grade,
        appointment_is_past=appointment_is_past,
        messages=messages,
        current_user_id=current_user_id,
    )


@app.route("/groups/<int:group_id>/join", methods=["POST"])
@login_required
def join_group(group_id):
    account_id = session["account_id"]

    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    if group.appointment and int(group.appointment) < int(time.time()):
        flash("Diese Lerngruppe ist bereits abgelaufen.", "warning")
        return redirect(url_for("index"))

    # Schon Mitglied?
    existing = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id,
        accepted=True
    ).first()
    if existing:
        flash("Du bist bereits Mitglied.", "info")
        return redirect(url_for("group_overview", group_id=group_id))

    member_count = GroupMemberModel.query.filter_by(group_id=group.id).count()

    if member_count >= MAX_GROUP_MEMBERS:
        flash("Die Gruppe ist bereits voll.", "info")
        return redirect(url_for("index"))

    # Mitglied anlegen
    member = GroupMemberModel(
        account_id=account_id,
        group_id=group_id,
    )

    db.session.add(member)
    db.session.commit()

    flash("Du bist der Gruppe beigetreten", "success")
    return redirect(url_for("group_overview", group_id=group_id))


@app.route("/groups/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    account_id = int(session["account_id"])

    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    membership = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id
    ).first()

    if not membership:
        flash("Du bist kein Mitglied dieser Gruppe.", "warning")
        return redirect(url_for("group_overview", group_id=group_id))

    if group.owner == account_id:
        flash("Als Gruppenleiter kannst du die Gruppe nicht verlassen. "
              "Du kannst sie nur löschen.", "warning")
        return redirect(url_for("group_overview", group_id=group_id))

    db.session.delete(membership)
    db.session.commit()

    flash("Du hast die Gruppe verlassen.", "success")
    return redirect(url_for("index"))


@app.route("/groups/create", methods=["POST"])
@login_required
def create_group():
    ok, errors = validate_text_fields(request.form, GROUP_TEXT_FIELDS)
    if not ok:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("index"))

    account_id = session["account_id"]
    group_count = GroupModel.query.filter_by(
        owner=account_id,
        is_active=True
    ).count()

    if group_count >= 5:
        flash("Du kannst maximal 5 Gruppen erstellen.", "warning")
        return redirect(url_for("index"))

    name = (request.form.get("name") or "").strip()
    klasse = (request.form.get("klasse") or "").strip()
    stufe = (request.form.get("stufe") or "").strip()
    fach = (request.form.get("fach") or "").strip()
    thema = (request.form.get("thema") or "").strip()
    appointment_raw = request.form.get("appointment")
    place = (request.form.get("place") or "").strip()

    appointment_ts = None
    if appointment_raw:
        dt = datetime.fromisoformat(appointment_raw)
        appointment_ts = int(dt.timestamp())

        if appointment_ts and appointment_ts < int(time.time()):
            flash("Der Treffpunkt darf nicht in der Vergangenheit liegen.", "danger")
            return redirect(url_for("index"))

    errors = []
    if len(name) < 2:
        errors.append("Gruppenname ist zu kurz.")
    if stufe not in ALLOWED_GRADES:
        errors.append("Ungültige Stufe.")
    if place not in {"Online", "Schule"}:
        errors.append("Ungültiger Ort gewählt.")

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("index"))

    group = GroupModel(
        owner=account_id,
        name=name,
        klasse=klasse or None,
        grade=stufe,
        subject=fach or None,
        topic=thema,
        appointment=appointment_ts,
        place=place,
    )

    save_group(group)
    db.session.add(GroupMemberModel(group_id=group.id, account_id=account_id, accepted=True))
    db.session.commit()

    flash("Gruppe erfolgreich erstellt.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/delete", methods=["POST"])
@login_required
def delete_group_route(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    account_id = session["account_id"]
    if group.owner != account_id:
        flash("Du darfst diese Gruppe nicht löschen.", "danger")
        return redirect(url_for("index"))

    # Löschen
    delete_group(group_id)

    flash("Gruppe wurde gelöscht.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/deactivate", methods=["POST"])
@login_required
def deactivate_group_route(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    account_id = session["account_id"]
    if group.owner != account_id:
        flash("Keine Berechtigung.", "danger")
        return redirect(url_for("index"))

    group.is_active = False
    db.session.commit()

    flash("Gruppe wurde deaktiviert.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/edit", methods=["POST"])
@login_required
def edit_group_route(group_id):
    ok, errors = validate_text_fields(request.form, GROUP_TEXT_FIELDS)
    if not ok:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("index"))

    group = db.session.get(GroupModel, group_id)
    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    account_id = session["account_id"]
    if group.owner != account_id:
        flash("Du darfst diese Gruppe nicht bearbeiten.", "danger")
        return redirect(url_for("index"))

    # POST: speichern
    name = (request.form.get("name") or "").strip()
    klasse = (request.form.get("klasse") or "").strip()
    stufe = (request.form.get("stufe") or "").strip()
    fach = (request.form.get("fach") or "").strip()
    thema = (request.form.get("thema") or "").strip()
    appointment_raw = request.form.get("appointment")
    place = (request.form.get("place") or "").strip()

    errors = []
    if appointment_raw:
        dt = datetime.fromisoformat(appointment_raw)
        group.appointment = int(dt.timestamp())

        if group.appointment and group.appointment < int(time.time()):
            flash("Der Treffpunkt darf nicht in der Vergangenheit liegen.", "danger")
            return redirect(url_for("index"))
    else:
        errors.append("Gib ein gültiges Datum ein!.")

    if len(name) < 2:
        errors.append("Bitte gib einen Gruppennamen (mind. 2 Zeichen) ein.")
    if stufe and stufe not in ALLOWED_GRADES:
        errors.append("Ungültige Stufe gewählt.")
    if place not in {"Online", "Schule"}:
        errors.append("Ungültiger Ort gewählt.")

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("edit_group_route", group_id=group.id))

    # Update (nur erlaubte Felder)
    group.name = name
    group.klasse = klasse or None
    group.grade = stufe or None
    group.subject = fach or None
    group.topic = thema or None
    group.place = place

    db.session.commit()

    flash("Gruppe wurde aktualisiert.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/messages", methods=["POST"])
@login_required
def send_group_message(group_id):
    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    if not require_membership(group_id):
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for("index"))

    text = (request.form.get("message") or "").strip()
    if contains_profanity(text):
        flash("Bitte keine Schimpfwörter in Nachrichten verwenden.", "danger")
        return redirect(url_for("group_overview", group_id=group_id))

    if not text:
        flash("Nachricht darf nicht leer sein.", "danger")
        return redirect(url_for("group_overview", group_id=group_id))

    if len(text) > 1000:
        flash("Nachricht ist zu lang (max. 1000 Zeichen).", "danger")
        return redirect(url_for("group_overview", group_id=group_id))

    account_id = session["account_id"]

    msg = GroupActionModel(
        group_id=group_id,
        account_id=account_id,
        type="MESSAGE",
        content=text,
    )
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for("group_overview", group_id=group_id))


@app.route("/admin", methods=['GET'])
@admin_required
def admin_dashboard():
    query = request.args.get("q")
    if query:
        users = (AccountModel.query
                 .filter(or_(
                    AccountModel.first_name.like("%" + query + "%"),
                    AccountModel.last_name.like("%" + query + "%")))
                 .all())
    else:
        users = AccountModel.query.all()
    return render_template(
        "dashboard.html",
        users=users,
    )


@app.route("/account/<int:user_id>/deactivate", methods=["GET", "POST"])
@admin_required
def account_deactivate(user_id):
    account = db.session.get(AccountModel, user_id)

    if not account:
        flash("Nutzer nicht gefunden.", "danger")
        return redirect(url_for("admin_dashboard"))

    account.is_active = False
    db.session.commit()

    flash("Nutzer wurde deaktiviert.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/account/<int:user_id>/activate", methods=["GET", "POST"])
@admin_required
def account_activate(user_id):
    account = db.session.get(AccountModel, user_id)

    if not account:
        flash("Nutzer nicht gefunden.", "danger")
        return redirect(url_for("admin_dashboard"))

    account.is_active = True
    db.session.commit()

    flash("Nutzer wurde aktiviert.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == '__main__':
    app.run(port=4000, debug=True)
