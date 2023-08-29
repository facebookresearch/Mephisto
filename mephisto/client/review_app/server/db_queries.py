from typing import Optional


def create_unit_review(
    db,
    unit_id: int,
    task_id: int,
    worker_id: int,
    status: str,
    feedback: Optional[str] = None,
    tips: Optional[str] = None,
) -> None:
    """ Create unit review in the db """

    with db.table_access_condition:
        conn = db._get_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO unit_review (
                unit_id,
                worker_id,
                task_id,
                status,
                feedback,
                tips
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                unit_id,
                worker_id,
                task_id,
                status,
                feedback,
                tips,
            ),
        )
        conn.commit()
