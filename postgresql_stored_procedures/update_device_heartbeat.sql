DROP PROCEDURE IF EXISTS update_device_heartbeat;

CREATE OR REPLACE PROCEDURE update_device_heartbeat(
    IN p_device_id TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO device_heartbeat (device_id, last_seen)
    VALUES (p_device_id, NOW())
    ON CONFLICT (device_id)
    DO UPDATE SET last_seen = EXCLUDED.last_seen;
END;
$$;