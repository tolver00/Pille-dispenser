import math
import server_logging

def test_resource_utilization():
        cpu, mem, disk, pids, uptime = server_logging.resource_utilization()
            
        # Percentages should be in 0–100
        assert isinstance(cpu, (int, float))
        assert 0.0 <= cpu <= 100.0

        assert isinstance(mem, (int, float))
        assert 0.0 <= mem <= 100.0

        assert isinstance(disk, (int, float))
        assert 0.0 <= disk <= 100.0

        # pids should be a positive integer
        assert isinstance(pids, int)
        assert pids > 0

        # uptime in hours should be positive
        assert isinstance(uptime, (int, float))
        assert uptime > 0
