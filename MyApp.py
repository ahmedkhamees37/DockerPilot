import json
import subprocess
import yaml
class MyApp: 
    def __init__(self, root):
        self.root = root
        self.top_bar = TopBar(root, self)

    def show_message(self, message):
        print(f"Button clicked: {message}")

    def run_code(self):
        # Your code to run when the "Start" button is clicked
        print("Running code...")

        # Network
        def get_network():
            dict1 = {}
            cmd = f'ls networks | wc -l'
            count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            for i in range(1, int(count.stdout.split()[0]) + 1):
                with open(f"/tmp/networks/network{i}.json", "r") as file:
                    data = json.load(file)[0]
                network_name = data["name"]
                subnet = data["subnet"]
                cmd = f'docker network ls | cut -d" " -f4 | grep -c ^{network_name}$'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if int(result.stdout.split()[0]) > 0:
                    dict1.update({network_name: {"external": "true"}})
                else:
                    dict1.update({network_name: {"driver": "bridge", "ipam": {"config": [{"subnet": subnet}]}}})
            return dict1

        # Volumes
        def get_volume():
            cmd = f'ls volumes | wc -l'
            count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            dict1 = {}
            for i in range(1, int(count.stdout.split()[0]) + 1):
                with open(f"/tmp/volume/volume{i}.json", "r") as file:
                    data = json.load(file)[0]
                volume_name = data["name"]
                cmd = f'docker volume ls | cut -d" " -f6 | grep -c "^{volume_name}$"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if int(result.stdout.split()[0]) > 0:
                    dict1.update({volume_name: {"external": "true"}})
                else:
                    dict1.update({volume_name: {}})
            return dict1

        # Services
        def get_service():
            dict1 = {}
            cmd = f'ls containers | wc -l'
            count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            for i in range(1, int(count.stdout.split()[0]) + 1):
                with open(f"/tmp/container/container{i}.json", "r") as file:
                    data = json.load(file)[0]
                image_name = data["image_name"]
                service_name = data["name"]
                container_name = data["name"]
                network_name = data["parent_network"]
                port_list = data["expose_port"]
                volumes_list = []
                for vol in data["volumes"]:
                    volume_name = vol["volume_name"]
                    mount_point = vol["mount_path"]
                    volumes_list.append(f"{volume_name}:{mount_point}")
                cmd = f"docker ps -a | awk '{{print $NF}}' | grep -c '^{container_name}$'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if int(result.stdout.split()[0]) > 0:
                    dict1.update({
                        service_name: {
                            "image": image_name,
                            "container_name": container_name + ".2",
                            "networks": [network_name],
                            "volumes": volumes_list,
                            "ports": [port_list]
                        }
                    })
                else:
                    dict1.update({
                        service_name: {
                            "image": image_name,
                            "container_name": container_name,
                            "networks": [network_name],
                            "volumes": volumes_list,
                            "ports": [port_list]
                        }
                    })
            return dict1

        networks = get_network()
        volumes = get_volume()
        services = get_service()

        compose = {
            "services": services,
            "networks": networks,
            "volumes": volumes
        }

        with open("compose.yml", "w") as file:
            yaml.dump(compose, file, sort_keys=False)
        print("Docker Compose file generated successfully: compose.yml")

        result = subprocess.run("docker-compose -f compose.yml up", shell=True, capture_output=True, text=True)
        print("Containers run successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
