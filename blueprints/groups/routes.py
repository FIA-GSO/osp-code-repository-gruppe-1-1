import time
from datetime import datetime

from flask import request, session, redirect, url_for, render_template, flash
from sqlalchemy.orm import joinedload

from database.model.base import db
from database.model.groupModel import GroupModel, save_group, delete_group
from database.model.groupMemberModel import GroupMemberModel
from database.model.accountModel import AccountModel
from database.model.groupActionModel import GroupActionModel

from utils.profanity import validate_text_fields, contains_profanity
from utils.profanity_config import GROUP_TEXT_FIELDS

from blueprints.groups import groups_bp
from blueprints.common import (
    login_required,
    require_membership,
    ALLOWED_GRADES,
    MAX_GROUP_MEMBERS,
)


@groups_bp.route("/groups/<int:group_id>", methods=["GET"])
@login_required
def group_overview(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    if not require_membership(group_id):
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for("main.index"))

    member_count = GroupMemberModel.query.filter_by(group_id=group.id).count()

    owner_account = db.session.get(AccountModel, group.owner)
    owner_first_name = owner_account.first_name.strip() if owner_account and owner_account.first_name else "Unbekannt"

    current_user_id = session.get("account_id")
    current_user = db.session.get(AccountModel, current_user_id)
    current_user_email = current_user.email.strip() if current_user and current_user.email else "Unbekannt"

    grade = group.grade

    now = int(time.time())
    appointment_is_past = bool(group.appointment and int(group.appointment) < now)

    messages = (
        GroupActionModel.query
        .options(joinedload(GroupActionModel.account))
        .filter_by(group_id=group_id, type="MESSAGE")
        .order_by(GroupActionModel.created.desc())
        .all()
    )

    return render_template(
        "group_overview.html",
        group=group,
        member_count=member_count,
        group_limit=MAX_GROUP_MEMBERS,
        owner_first_name=owner_first_name,
        grade=grade,
        appointment_is_past=appointment_is_past,
        messages=messages,
        current_user=current_user,
        current_user_id=current_user_id,
        current_user_email=current_user_email,
    )


@groups_bp.route("/groups/<int:group_id>/join", methods=["POST"])
@login_required
def join_group(group_id):
    account_id = session["account_id"]

    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    if group.appointment and int(group.appointment) < int(time.time()):
        flash("Diese Lerngruppe ist bereits abgelaufen.", "warning")
        return redirect(url_for("main.index"))

    # Schon Mitglied?
    existing = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id,
        accepted=True
    ).first()
    if existing:
        flash("Du bist bereits Mitglied.", "info")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    member_count = GroupMemberModel.query.filter_by(group_id=group.id).count()
    if member_count >= MAX_GROUP_MEMBERS:
        flash("Die Gruppe ist bereits voll.", "info")
        return redirect(url_for("main.index"))

    member = GroupMemberModel(account_id=account_id, group_id=group_id)
    db.session.add(member)
    db.session.commit()

    flash("Du bist der Gruppe beigetreten", "success")
    return redirect(url_for("groups.group_overview", group_id=group_id))


@groups_bp.route("/groups/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    account_id = int(session["account_id"])

    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    membership = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id
    ).first()

    if not membership:
        flash("Du bist kein Mitglied dieser Gruppe.", "warning")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    if group.owner == account_id:
        flash("Als Gruppenleiter kannst du die Gruppe nicht verlassen. Du kannst sie nur löschen.", "warning")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    db.session.delete(membership)
    db.session.commit()

    flash("Du hast die Gruppe verlassen.", "success")
    return redirect(url_for("main.index"))


@groups_bp.route("/groups/create", methods=["POST"])
@login_required
def create_group():
    ok, errors = validate_text_fields(request.form, GROUP_TEXT_FIELDS)
    if not ok:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("main.index"))

    account_id = session["account_id"]

    group_count = GroupModel.query.filter_by(owner=account_id, is_active=True).count()
    if group_count >= 5:
        flash("Du kannst maximal 5 Gruppen erstellen.", "warning")
        return redirect(url_for("main.index"))

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

        if appointment_ts < int(time.time()):
            flash("Der Treffpunkt darf nicht in der Vergangenheit liegen.", "danger")
            return redirect(url_for("main.index"))

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
        return redirect(url_for("main.index"))

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
    return redirect(url_for("main.index"))


@groups_bp.route("/groups/<int:group_id>/delete", methods=["POST"])
@login_required
def delete_group_route(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    account_id = session["account_id"]
    user = AccountModel.query.get(account_id)

    if group.owner != account_id | user.role != "ADMIN":
        flash("Du darfst diese Gruppe nicht löschen.", "danger")
        return redirect(url_for("main.index"))

    delete_group(group_id)

    flash("Gruppe wurde gelöscht.", "success")
    return redirect(url_for("main.index"))


@groups_bp.route("/groups/<int:group_id>/deactivate", methods=["POST"])
@login_required
def deactivate_group_route(group_id):
    group = db.session.get(GroupModel, group_id)

    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    account_id = session["account_id"]
    if group.owner != account_id:
        flash("Keine Berechtigung.", "danger")
        return redirect(url_for("main.index"))

    group.is_active = False
    db.session.commit()

    flash("Gruppe wurde deaktiviert.", "success")
    return redirect(url_for("main.index"))


@groups_bp.route("/groups/<int:group_id>/edit", methods=["POST"])
@login_required
def edit_group_route(group_id):
    ok, errors = validate_text_fields(request.form, GROUP_TEXT_FIELDS)
    if not ok:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("main.index"))

    group = db.session.get(GroupModel, group_id)
    if not group:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    account_id = session["account_id"]
    if group.owner != account_id:
        flash("Du darfst diese Gruppe nicht bearbeiten.", "danger")
        return redirect(url_for("main.index"))

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
        if group.appointment < int(time.time()):
            flash("Der Treffpunkt darf nicht in der Vergangenheit liegen.", "danger")
            return redirect(url_for("main.index"))
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
        return redirect(url_for("main.index"))

    group.name = name
    group.klasse = klasse or None
    group.grade = stufe or None
    group.subject = fach or None
    group.topic = thema or None
    group.place = place

    db.session.commit()

    flash("Gruppe wurde aktualisiert.", "success")
    return redirect(url_for("main.index"))


@groups_bp.route("/groups/<int:group_id>/messages", methods=["POST"])
@login_required
def send_group_message(group_id):
    group = db.session.get(GroupModel, group_id)
    if not group or not group.is_active:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for("main.index"))

    if not require_membership(group_id):
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for("main.index"))

    text = (request.form.get("message") or "").strip()

    if contains_profanity(text):
        flash("Bitte keine Schimpfwörter in Nachrichten verwenden.", "danger")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    if not text:
        flash("Nachricht darf nicht leer sein.", "danger")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    if len(text) > 1000:
        flash("Nachricht ist zu lang (max. 1000 Zeichen).", "danger")
        return redirect(url_for("groups.group_overview", group_id=group_id))

    account_id = session["account_id"]

    msg = GroupActionModel(
        group_id=group_id,
        account_id=account_id,
        type="MESSAGE",
        content=text,
    )
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for("groups.group_overview", group_id=group_id))
