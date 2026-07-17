from flask import Blueprint, abort, jsonify
from sqlalchemy import select

from app.extensions import db
from app.models import School

from . import bp


@bp.get("/school/<int:school_code>")
def get_school(school_code: int):

    school = db.session.scalar(
        select(School).where(
            School.school_code == school_code
        )
    )

    if school is None:
        abort(404)

    return jsonify(
        {
            "school_code": school.school_code,
            "name": school.name,
            "town": school.town_suburb,
            "postcode": school.postcode,
            "latitude": school.latitude,
            "longitude": school.longitude,
            "transfer_points": school.transfer_points,
            "school_type": school.school_type.code,
        }
    )


@bp.get("/schools")
def get_schools():

    schools = db.session.scalars(
        select(School)
    ).all()

    return jsonify(
        [
            {
                "school_code": school.school_code,
                "name": school.name,
                "latitude": school.latitude,
                "longitude": school.longitude,
    "school_type": school.school_type.code,
            }
            for school in schools
        ]
    )