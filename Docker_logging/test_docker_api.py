import docker
from datetime import datetime
import requests

DockerENV = docker.from_env()
ContainerList = DockerENV.containers.list(all=True)

try:

    for Container in ContainerList:
        DictNetData = {}

        ContainerStartTimeEpoch = (datetime.strptime((Container.attrs['State']['StartedAt'])[:26],'%Y-%m-%dT%H:%M:%S.%f')).timestamp()
        EpochSecNow = datetime.now().timestamp()
        ContainerStatus = str(Container.attrs['State']['Status'])
        ContainerName = str(Container.name)

        if ContainerStatus == 'running':
            ContainerStats = Container.stats(stream=False)

            ContainerUptime = int((EpochSecNow - ContainerStartTimeEpoch) / (60*60))
            MemoryBytesUsed = ContainerStats['memory_stats']['usage']

            # Calculating actual usage at runtime in percent
            ContainerCpuUsageTotal = ContainerStats['cpu_stats']['cpu_usage']['total_usage'] - ContainerStats['precpu_stats']['cpu_usage']['total_usage']
            SystemCpuUsageTotal = ContainerStats['cpu_stats']['system_cpu_usage'] - ContainerStats['precpu_stats']['system_cpu_usage']
            ContainerCpuPercent = round((ContainerCpuUsageTotal / SystemCpuUsageTotal) * 100, 3)


            # Network stats for container
            for NetData in ContainerStats['networks']['eth0']:
                if NetData == 'rx_bytes' or NetData == 'tx_bytes':
                    continue
                DictNetData.update({NetData:int(ContainerStats['networks']['eth0'][NetData])})


            # Send container stats
            DataToSend = {
                'in_uptime_hours' : ContainerUptime,
                'in_container_name' : ContainerName,
                'in_container_status' : ContainerStatus,
                'in_time_epoch' : EpochSecNow,
                'in_cpu_usage' : ContainerCpuPercent,
                'in_ram_usage_bytes' : MemoryBytesUsed,
                'in_rx_packets' : DictNetData['rx_packets'],
                'in_rx_dropped' : DictNetData['rx_dropped'],
                'in_rx_errors' : DictNetData['rx_errors'],
                'in_tx_packets' : DictNetData['tx_packets'],
                'in_tx_dropped' : DictNetData['tx_dropped'],
                'in_tx_errors' : DictNetData['tx_errors']
            }

            requests.post("http://172.20.0.2:41000/add_docker_logs", json=DataToSend)
            print(DataToSend)

except Exception as e:
    print("an error has occoured:", e)