from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from common.models import Field, AnonymizationMethod, FieldAnonymization
from webapp.forms import AnonymizationForm
from common.extensions import db
import json

anonymization_bp = Blueprint("anonymization", __name__)

@anonymization_bp.route("/edit_anonymization/<int:field_id>", methods=["GET", "POST"])
def edit_anonymization(field_id):
    field = Field.query.get_or_404(field_id)
    endpoint = field.endpoint
    swagger = endpoint.swagger
    example_value = None

    try:
        swagger_data = json.loads(swagger.raw_json)
        path_info = swagger_data['paths'].get(endpoint.path, {}).get(endpoint.method.lower(), {})
        if field.is_response_field:
            for response in path_info.get('responses', {}).values():
                content = response.get('content', {}).get('application/json', {})
                if 'example' in content:
                    if isinstance(content['example'], list) and content['example']:
                        example_value = content['example'][0].get(field.name)
                    elif isinstance(content['example'], dict):
                        example_value = content['example'].get(field.name)
        else:
            request_body = path_info.get('requestBody', {}).get('content', {}).get('application/json', {})
            if 'schema' in request_body and 'properties' in request_body['schema']:
                example_value = request_body['schema']['properties'].get(field.name, {}).get('example')
    except Exception as e:
        print(f"Error parsing Swagger JSON: {e}")

    form = AnonymizationForm()
    if request.method == 'GET':
        if field.anonymization and field.anonymization.anonymization_method:
            form.category.data = field.anonymization.anonymization_method.category
        form.data_category.data = field.data_category

    if request.method == 'POST':
        method_id = request.form.get('anonymization_method')
        if not method_id:
            flash("Please select an anonymization method", "danger")
            return redirect(url_for('anonymization.edit_anonymization', field_id=field.id))

        method = AnonymizationMethod.query.get(method_id)
        if not method:
            flash("Invalid method selected", "danger")
            return redirect(url_for('anonymization.edit_anonymization', field_id=field.id))

        if not field.anonymization:
            field.anonymization = FieldAnonymization(field_id=field.id)
            db.session.add(field.anonymization)

        field.anonymization.anonymization_method_id = method.id
        field.data_category = form.data_category.data

        try:
            db.session.commit()
            flash("Anonymization method updated successfully!", "success")
            return redirect(url_for("swagger.swagger_details", id=endpoint.swagger_id, _anchor=f"endpoint-{endpoint.id}"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving changes: {str(e)}", "danger")

    hide_category_field = False
    if field.anonymization and field.anonymization.anonymization_method:
        hide_category_field = field.anonymization.anonymization_method.name in ['Hashing', 'Encryption']

    return render_template("edit_anonymization.html", form=form, field=field, endpoint=endpoint, swagger=swagger, example_value=example_value, current_method=field.anonymization.anonymization_method if field.anonymization else None, hide_category_field=hide_category_field)

@anonymization_bp.route('/get_anonymization_methods', methods=['POST'])
def get_anonymization_methods():
    data = request.get_json()
    methods = AnonymizationMethod.query.filter_by(category=data['category']).all()
    return jsonify([{'id': m.id, 'name': m.name} for m in methods])
