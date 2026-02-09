from flask import Flask, request, session, redirect, url_for, render_template, jsonify, flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from datetime import datetime
import time
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload

from database.model.base import db
from database.model.groupModel import GroupModel, save_group, delete_group
from services.accountService import create_account as service_create_account, login_user as service_login_user
from database.model.groupActionModel import GroupActionModel

ALLOWED_GRADES = {"Unterstufe", "Mittelstufe", "Oberstufe"}

app = Flask(__name__)
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
    if session.get('account', None) is not None:
        search = (request.args.get("q") or "").strip()

        query = GroupModel.query.filter_by(is_active=True)

        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    GroupModel.subject.ilike(like),
                    GroupModel.topic.ilike(like),
                )
            )

        groups = query.order_by(GroupModel.appointment.desc()).all()

        now = int(time.time())
        today = datetime.now().date()

        group_meta = {}

        for g in groups:
            status = None  # None | today | past | future

            # Platzhalter (später echte Member-Zahl)
            member_count = 2  # Hier member anzahl aus db holen
            group_limit = 32
            is_full = member_count >= group_limit

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
                "group_limit": group_limit,
                "is_full": is_full,
            }

        return render_template(
            "index.html",
            groups=groups,
            group_meta=group_meta,
            search=search,
        )
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@app.route("/login_user", methods=['POST'])
def login_user():
    service_login_user()
    return redirect(url_for('index'))


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('account', None)
    flash('Erfolgreich ausgeloggt!', "success")
    return redirect(url_for('index'))


@app.route("/register_account", methods=['GET'])
def register_account():
    return render_template('register.html')


@app.route("/create_account", methods=['POST'])
def create_account():
    service_create_account()
    return redirect(url_for('index'))


@app.route("/groups/<int:group_id>", methods=["GET"])
def group_overview(group_id):
    # Gruppe laden
    group = GroupModel.query.get(group_id)

    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    # --- Platzhalter / vorbereitete Werte ---
    # Später: echte Member-Tabelle
    member_count = 2  # TODO: dynamisch
    group_limit = 32

    # Später: Owner aus Account-Tabelle laden
    owner_name = "Max Mustermann"

    # Anzeige zusammenbauen
    class_grade = f"{group.klasse or '-'} / {group.grade or '-'}"

    now = int(time.time())
    appointment_is_past = bool(group.appointment and int(group.appointment) < now)

    messages = (
        GroupActionModel.query
        .options(joinedload(GroupActionModel.account))
        .filter_by(group_id=group_id, type="MESSAGE")
        .order_by(GroupActionModel.created.asc())
        .all()
    )

    current_user_id = session.get("account")

    return render_template(
        "group_overview.html",
        group=group,
        member_count=member_count,
        group_limit=group_limit,
        owner_name=owner_name,
        class_grade=class_grade,
        appointment_is_past=appointment_is_past,
        messages=messages,
        current_user_id=current_user_id,
    )


@app.route("/groups/<int:group_id>/join", methods=["POST"])
def join_group(group_id):
    # TODO: hier später Membership in DB speichern
    flash("Beitreten ist noch nicht implementiert.", "info")
    return redirect(url_for("index"))


@app.route("/groups/create", methods=["POST"])
def create_group():
    # @todo:User checken ob schon 5 gruppen erstellt
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
        owner=1,  # später current_user.id
        name=name,
        klasse=klasse or None,
        grade=stufe,
        subject=fach or None,
        topic=thema,
        appointment=appointment_ts,
        place=place,
    )

    save_group(group)

    flash("Gruppe erfolgreich erstellt.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/delete", methods=["POST"])
def delete_group_route(group_id):
    # Gruppe laden
    group = GroupModel.query.get(group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    # ❗ Sicherheitscheck (Owner)
    # aktuell hast du noch kein Login → daher Beispiel mit owner == 1
    # später: current_user.id
    if group.owner != 1:
        flash("Du darfst diese Gruppe nicht löschen.", "danger")
        return redirect(url_for("index"))

    # Löschen
    delete_group(group_id)

    flash("Gruppe wurde gelöscht.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/deactivate", methods=["POST"])
def deactivate_group_route(group_id):
    group = GroupModel.query.get(group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    if group.owner != 1:
        flash("Keine Berechtigung.", "danger")
        return redirect(url_for("index"))

    group.is_active = False
    db.session.commit()

    flash("Gruppe wurde deaktiviert.", "success")
    return redirect(url_for("index"))


@app.route("/groups/<int:group_id>/edit", methods=["GET", "POST"])
def edit_group_route(group_id):
    group = GroupModel.query.get(group_id)
    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    # TODO: später current_user.id
    owner_id = 1
    if group.owner != owner_id:
        flash("Du darfst diese Gruppe nicht bearbeiten.", "danger")
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("group_edit.html", group=group)

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
def send_group_message(group_id):
    if session.get("account") is None:
        flash("Bitte zuerst einloggen.", "danger")
        return redirect(url_for("login"))

    group = GroupModel.query.get(group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("index"))

    text = (request.form.get("message") or "").strip()
    if not text:
        flash("Nachricht darf nicht leer sein.", "danger")
        return redirect(url_for("group_overview", group_id=group_id))

    if len(text) > 1000:
        flash("Nachricht ist zu lang (max. 1000 Zeichen).", "danger")
        return redirect(url_for("group_overview", group_id=group_id))

    account_id = session.get("account")
    if account_id is None:
        flash("Ungültige Session.", "danger")
        return redirect(url_for("login"))

    msg = GroupActionModel(
        group_id=group_id,
        account_id=account_id,
        type="MESSAGE",
        content=text,
    )
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for("group_overview", group_id=group_id))

if __name__ == '__main__':
    app.run(port=4000, debug=True)
