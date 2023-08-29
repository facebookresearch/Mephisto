from flask import Flask

from .api import views as api_views


def init_urls(app: Flask):
    app.add_url_rule(
        "/qualifications/<int:qualification_id>/workers",
        view_func=api_views.QualificationWorkersView.as_view("qualification_workers"),
    )
    app.add_url_rule(
        "/qualifications/<int:qualification_id>/workers/<int:worker_id>/grant",
        view_func=api_views.QualifyWorkerView.as_view("qualification_worker_grant"),
        defaults={"action": "grant"},
    )
    app.add_url_rule(
        "/qualifications/<int:qualification_id>/workers/<int:worker_id>/revoke",
        view_func=api_views.QualifyWorkerView.as_view("qualification_worker_revoke"),
        defaults={"action": "revoke"},
    )
    app.add_url_rule(
        "/qualifications/",
        view_func=api_views.QualificationsView.as_view("qualifications"),
    )
    app.add_url_rule(
        "/tasks/",
        view_func=api_views.TasksView.as_view("tasks"),
    )
    app.add_url_rule(
        "/tasks/<int:task_id>/worker-units-ids",
        view_func=api_views.TasksWorkerUnitsView.as_view("worker-units-ids"),
    )
    app.add_url_rule(
        "/units",
        view_func=api_views.UnitsView.as_view("units"),
    )
    app.add_url_rule(
        "/units/details",
        view_func=api_views.UnitsDetailsView.as_view("units_details"),
    )
    app.add_url_rule(
        "/units/approve",
        view_func=api_views.UnitsApproveView.as_view("units_approve"),
    )
    app.add_url_rule(
        "/units/reject",
        view_func=api_views.UnitsRejectView.as_view("units_reject"),
    )
    app.add_url_rule(
        "/units/soft-reject",
        view_func=api_views.UnitsSoftRejectView.as_view("units_soft_reject"),
    )
    app.add_url_rule(
        "/workers/<int:worker_id>/block",
        view_func=api_views.WorkerBlockView.as_view("worker_block"),
    )
    app.add_url_rule(
        "/workers/<int:worker_id>/stats",
        view_func=api_views.WorkerStatsView.as_view("worker_stats"),
    )
