CREATE OR REPLACE PROCEDURE add_docker_logs(
    IN  in_time_epoch      	DOUBLE PRECISION,
    IN  in_container_name  	VARCHAR(100),
    IN  in_container_status	VARCHAR(100),
    IN  in_uptime_hours    	INTEGER,
    IN  in_cpu_usage       	FLOAT4,
    IN  in_ram_usage_bytes 	INTEGER,
    IN  in_rx_packets 		INTEGER,
    IN  in_rx_dropped 		INTEGER,
    IN  in_rx_errors  		INTEGER,
    IN  in_tx_packets 		INTEGER,
    IN  in_tx_dropped 		INTEGER,
    IN  in_tx_errors  		INTEGER
)

LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO docker_logs(
		time_epoch,
	   	container_name,
		container_status,
		uptime_hours,
		cpu_usage,
		ram_usage_bytes,
		rx_packets,
		rx_dropped,
		rx_errors,
		tx_packets,
		tx_dropped,
		tx_errors
	)
    VALUES (
		in_time_epoch,
	   	in_container_name,
		in_container_status,
		in_uptime_hours,
		in_cpu_usage,
		in_ram_usage_bytes,
		in_rx_packets,
		in_rx_dropped,
		in_rx_errors,
		in_tx_packets,
		in_tx_dropped,
		in_tx_errors
	);
END;
$$;