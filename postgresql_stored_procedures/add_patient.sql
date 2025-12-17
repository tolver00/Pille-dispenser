CREATE OR REPLACE PROCEDURE add_patient(
    IN  p_first_name TEXT,
    IN  p_last_name  TEXT,
    IN  p_age        INTEGER,
    IN  p_blood_type TEXT,
    IN  p_allergies  TEXT,
    INOUT p_new_id   INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO patients (first_name, last_name, age, blood_type, allergies)
    VALUES (p_first_name, p_last_name, p_age, p_blood_type, p_allergies)
    RETURNING id INTO p_new_id;
END;
$$;