# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user

from enma.activity.models import Activity
from enma.database import db


blueprint = Blueprint("activity", __name__, url_prefix='/activities',
                        static_folder="../static")

class Columns():
    actor = False
    act_on = False
    category = True
    origin = False

@blueprint.route("/")
@login_required
def home():
    columns = Columns()
    activities = db.session.query(Activity)
    if current_user.is_administrator():
        columns.actor = True
        columns.act_on = True
        columns.origin = True
    else:
        activities = activities.filter_by(actor=current_user.username)
    activities = activities.order_by(Activity.timestamp.desc()).all()
    return render_template("activities/list.html", 
                           activities=activities,
                           columns=columns)


