from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from webapp.forms import SwaggerForm
from common.models import SwaggerAPI, Endpoint, Field, FieldAnonymization
from common.extensions import db
from .utils import parse_openapi
import json
import secrets
from uuid import uuid4


swagger_bp = Blueprint("swagger", __name__)

@swagger_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = SwaggerForm()
    if request.method == "GET":
        form.service_uuid.data = str(uuid4())

    if form.validate_on_submit():
        try:
            parsed_data = json.loads(form.swagger_json.data)

            if SwaggerAPI.query.filter_by(api_url=form.api_url.data, user_id=current_user.id).first():
                flash("API URL already exists!", "warning")
                return redirect(url_for("swagger.index"))

            swagger = SwaggerAPI(
                api_url=form.api_url.data,
                service_uuid=form.service_uuid.data,
                raw_json=form.swagger_json.data,
                encryption_key=secrets.token_hex(32),
                user_id=current_user.id
            )
            db.session.add(swagger)
            db.session.commit()

            parse_openapi(swagger, parsed_data)
            db.session.commit()

            flash(f"Swagger uploaded! Service UUID: {form.service_uuid.data}", "success")
            return redirect(url_for("swagger.index"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    user_swaggers = SwaggerAPI.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", form=form, swaggers=user_swaggers)

@swagger_bp.route("/swagger/<int:id>")
@login_required
def swagger_details(id):
    swagger = SwaggerAPI.query.get_or_404(id)
    endpoints = Endpoint.query.filter_by(swagger_id=id).all()
    return render_template("swagger_details.html", swagger=swagger, endpoints=endpoints)

# @swagger_bp.route("/delete_swagger/<int:id>", methods=["POST"])
# @login_required
# def delete_swagger(id):
#     swagger = SwaggerAPI.query.get_or_404(id)
#     endpoints = Endpoint.query.filter_by(swagger_id=id).all()
#     for endpoint in endpoints:
#         fields = Field.query.filter_by(endpoint_id=endpoint.id).all()
#         for field in fields:
          
#             FieldAnonymization.query.filter_by(field_id=field.id).delete()
#             db.session.delete(field)
#         db.session.delete(endpoint)

#     db.session.delete(swagger)
#     db.session.commit()

#     flash("Swagger configuration deleted successfully!", "success")
#     return redirect(url_for("swagger.index"))


@swagger_bp.route("/delete_swagger/<int:id>", methods=["POST"])
@login_required
def delete_swagger(id):
    swagger = SwaggerAPI.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    endpoints = Endpoint.query.filter_by(swagger_id=id).all()
    try:
        for endpoint in endpoints:
            fields = Field.query.filter_by(endpoint_id=endpoint.id).all()
            for field in fields:
                FieldAnonymization.query.filter_by(field_id=field.id).delete()
                db.session.delete(field)
            db.session.delete(endpoint)

        db.session.delete(swagger)
        db.session.commit()

        flash("Swagger configuration deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting swagger: {str(e)}", "danger")

    return redirect(url_for("swagger.index"))
