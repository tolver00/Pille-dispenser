CREATE OR REPLACE PROCEDURE get_patient_with_records(
    IN p_id INTEGER,
    INOUT p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_cursor IS NULL THEN
        p_cursor := 'patient_records_cursor';
    END IF;

    OPEN p_cursor FOR
        SELECT
            p.id          AS patient_id,
            p.first_name,
            p.last_name,
            pr.device_id,
            pr.start_date,
            pr.end_date,
            pr.timestamps,
            pr.pill_count
        FROM patients p
        JOIN patient_records pr
            ON p.id = pr.patient_id
        WHERE p.id = p_id;
END;
$$;