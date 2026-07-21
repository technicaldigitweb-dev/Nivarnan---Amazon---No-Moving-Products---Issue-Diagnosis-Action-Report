"""
publish_to_ph_task.py -- REQ-AMZ-NMP-001-D01

Publishes the validated report HTML to tech_team_outputs.ph_task, following
08_SKILLS/ph_task_reference/ (append-only versioning: insert a new row per
release, set version_status='rejected' on the prior active row -- never
UPDATE the old row's content).

HARD GATE: this module refuses to run unless every required ph_task metadata
field is supplied AND an explicit publish-approval flag is set. As of
2026-07-17 this decision (DEC-TECH-001 in the decision register) is OPEN --
this module has NOT been invoked and MUST NOT be invoked until Sajeesan or an
assigned technical reviewer approves the exact metadata values below.
"""

REQUIRED_METADATA_FIELDS = [
    "project_name", "project_code", "task_name", "team",
    "developer", "assigned_user", "assigned_user_team",
    "phase_level", "version_level",
]


class PublicationBlocked(Exception):
    pass


def publish(conn, html_content, metadata, publish_approved=False):
    """
    conn: a live database connection (see db_connection.py) -- not created or
          used by this session.
    html_content: the validated report HTML string.
    metadata: dict with keys from REQUIRED_METADATA_FIELDS.
    publish_approved: must be explicitly True, set only after DEC-TECH-001 is
          approved and a human has explicitly instructed publication.
    """
    missing = [f for f in REQUIRED_METADATA_FIELDS if not metadata.get(f)]
    if missing:
        raise PublicationBlocked(
            f"Refusing to publish: ph_task metadata fields not provided: {missing}. "
            "See decision register DEC-TECH-001."
        )
    if metadata.get("assigned_user_team") not in ("ph_priors", "ebay_priors"):
        raise PublicationBlocked(
            "assigned_user_team must be exactly 'ph_priors' or 'ebay_priors' "
            "per 08_SKILLS/ph_task_reference/ph_task_assigned_user_team_rules.md"
        )
    if not publish_approved:
        raise PublicationBlocked(
            "publish_approved flag is False -- publication was not explicitly "
            "instructed. This is a deliberate hard stop, not a bug."
        )

    with conn.cursor() as cur:
        # Step 1: supersede the prior active row for this project_code/task_name, if any.
        cur.execute(
            """
            UPDATE tech_team_outputs.ph_task
            SET version_status = 'rejected'
            WHERE project_code = %s AND task_name = %s AND version_status = 'released'
            """,
            (metadata["project_code"], metadata["task_name"]),
        )

        # Step 2: insert the new version (append-only -- never overwrite prior content).
        cur.execute(
            """
            INSERT INTO tech_team_outputs.ph_task
                (project_name, project_code, task_name, team, developer,
                 assigned_user, assigned_user_team, html_content, description,
                 phase_level, version_level, version_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'released')
            RETURNING id
            """,
            (
                metadata["project_name"], metadata["project_code"], metadata["task_name"],
                metadata["team"], metadata["developer"], metadata["assigned_user"],
                metadata["assigned_user_team"], html_content,
                metadata.get("description", ""),
                metadata["phase_level"], metadata["version_level"],
            ),
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id


def verify_publication(conn, new_id):
    """Read-only verification query, per instruction Step 15."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, assigned_user, assigned_user_team, project_code,
                   version_status, LENGTH(html_content) AS html_length,
                   created_at, updated_at, version_level
            FROM tech_team_outputs.ph_task
            WHERE id = %s
            """,
            (new_id,),
        )
        return cur.fetchone()


if __name__ == "__main__":
    raise SystemExit(
        "This module is not executed as part of the 2026-07-17 implementation "
        "session. DEC-TECH-001 (ph_task metadata) is OPEN. Do not run this "
        "script until that decision is approved and publication is explicitly instructed."
    )
