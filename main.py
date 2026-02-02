from flask import Flask, request, session, redirect, url_for, render_template, jsonify, flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from database.model.base import db
from database.model.groupModel import GroupModel, save_group, delete_group

ALLOWED_GRADES = {"Unterstufe", "Mittelstufe", "Oberstufe"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "dlajwasdhdddqwf98fg9f23803f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


csrf = CSRFProtect(app)

db.init_app(app)
with app.app_context():
    db.create_all()

# @todo UHRZEIT TREFFPUNKT DATENBANK!!!!!!!!


# Optional aber sehr empfehlenswert: CSRF Fehler hübsch behandeln
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("Sicherheitscheck fehlgeschlagen (CSRF). Bitte Seite neu laden und erneut versuchen.", "danger")
    return redirect(url_for("index"))


@app.route("/", methods=['GET'])
def index():
    groups = GroupModel.query.filter_by(is_active=True).order_by(GroupModel.created.desc()).all()
    return render_template("index.html", groups=groups)


@app.route("/groups/<int:group_id>/join", methods=["POST"])
def join_group(group_id):
    # TODO: hier später Membership in DB speichern
    flash("Beitreten ist noch nicht implementiert.", "info")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    # TODO: logout
    flash("logout ist noch nicht implementiert.", "info")
    return redirect(url_for("index"))


@app.route("/groups/create", methods=["POST"])
def create_group():
    # @todo:User checken ob schon 5 gruppen erstellt
    name = (request.form.get("name") or "").strip()
    klasse = (request.form.get("klasse") or "").strip()
    stufe = (request.form.get("stufe") or "").strip()
    fach = (request.form.get("fach") or "").strip()
    thema = (request.form.get("thema") or "").strip()

    errors = []
    if len(name) < 2:
        errors.append("Gruppenname ist zu kurz.")
    if stufe not in ALLOWED_GRADES:
        errors.append("Ungültige Stufe.")

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
        topic=thema or None,
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

    errors = []
    if len(name) < 2:
        errors.append("Bitte gib einen Gruppennamen (mind. 2 Zeichen) ein.")
    if stufe and stufe not in ALLOWED_GRADES:
        errors.append("Ungültige Stufe gewählt.")

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

    db.session.commit()

    flash("Gruppe wurde aktualisiert.", "success")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(port=4000, debug=True)


