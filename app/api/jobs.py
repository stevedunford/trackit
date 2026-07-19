from flask import Blueprint, jsonify

from app.models.vacancy import Vacancy

bp = Blueprint("jobs", __name__)


@bp.get("/")
def get_jobs():

    jobs = (
        Vacancy.query
        .filter_by(active=True)
        .all()
    )

    return jsonify([
        {
            "id": job.id,
            "title": job.title,
            "school_name": job.school.name,
            "school_type": job.school.school_type,
            "latitude": job.school.latitude,
            "longitude": job.school.longitude,
            "employment_type": job.employment_type.value,
            "closing_date": (
                job.closing_date.isoformat()
                if job.closing_date
                else None
            ),
            "recruitment_bonus": job.recruitment_bonus,
            "incentive_points": job.school.transfer_points,
        }
        for job in jobs
    ])
