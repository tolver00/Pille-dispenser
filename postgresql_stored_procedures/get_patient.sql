DROP PROCEDURE IF EXISTS get_patient;

CREATE OR REPLACE PROCEDURE get_patient(
    IN p_id INTEGER,
    INOUT p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_cursor IS NULL THEN
        p_cursor := 'patient_cursor';
    END IF;

    OPEN p_cursor FOR
        SELECT *
        FROM patients
        WHERE id = p_id;
END;
$$;