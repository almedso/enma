# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
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
    if current_user.is_administrator():
        columns.actor = True
        columns.act_on = True
        columns.origin = True
        activities = Activity.query
    else:
        activities = Activity.query.filter_by(actor=current_user.username)
    page = request.args.get('page', 1, type=int)
    pagination = activities.order_by(Activity.timestamp.desc()).paginate(
                page, per_page=10, error_out=False)
    print dir(pagination)
    return render_template("activities/list.html", 
                           #activities=activities,
                           activities=pagination.items,
                           pagination=pagination,
                           columns=columns)


