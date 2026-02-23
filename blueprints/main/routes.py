import time
from datetime import datetime
from flask import request, session, redirect, url_for, render_template
from sqlalchemy import or_

from database.model.base import db
from database.model.groupModel import GroupModel
from database.model.groupMemberModel import GroupMemberModel
from database.model.accountModel import AccountModel
from blueprints.main import main_bp
from blueprints.common import MAX_GROUP_MEMBERS


@main_bp.app_template_filter("dt_local")
def dt_local(unix_ts):
    if not unix_ts:
        return ""
    try:
        dt = datetime.fromtimestamp(int(unix_ts))
        return dt.strftime("%d.%m.%Y · %H:%M")
    except Exception:
        return ""


@main_bp.route("/", methods=["GET"])
def index():
    if not session.get("account_id"):
        return redirect(url_for("auth.login"))

    account_id = session.get("account_id")
    search = (request.args.get("q") or "").strip()

    query = GroupModel.query.filter_by(is_active=True)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(GroupModel.subject.ilike(like), GroupModel.topic.ilike(like)))

    groups = query.order_by(GroupModel.appointment.desc()).all()

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
        like = f"%{search}%"
        query_my = query_my.filter(or_(GroupModel.subject.ilike(like), GroupModel.topic.ilike(like)))

    my_groups = query_my.order_by(GroupModel.created.desc()).all()

    now = int(time.time())
    today = datetime.now().date()

    current_user = db.session.get(AccountModel, account_id)
    user_email = current_user.email.strip() if current_user and current_user.email else "Unbekannt"

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
        user_email=user_email,
        current_user=current_user,
    )
