from datasets import load_dataset
import docker
import time
import random
client = docker.from_env()

dataset_path = "princeton-nlp/SWE-Bench_Lite"
dataset_path = "swe-bench/SWE-Bench_Multilingual"
dataset_path = "princeton-nlp/SWE-Bench_Verified"
instances = list(load_dataset(dataset_path, split="test"))


# dockerhub has ratelimiting for unauthenticated users
# clean up if disk is full
# docker rmi -f $(docker images "swebench/*" -q)

def image_exists_on_hub(image_name):
    try:
        client.images.get_registry_data(image_name)
        return True
    except:
        return False 

def get_swebench_docker_image_name(instance: dict) -> str:
    """Get the image name for a SWEBench instance."""
    image_name = instance.get("image_name", None) or instance.get("docker_image", None)
    if image_name is None:
        # Docker doesn't allow double underscore, so we replace them with a magic token
        iid = instance["instance_id"]
        id_docker_compatible = iid.replace("__", "_1776_")
        image_name = f"docker.io/swebench/sweb.eval.x86_64.{id_docker_compatible}:latest".lower()
    return image_name

for idx,instance in enumerate(instances):
    image_name = get_swebench_docker_image_name(instance)
    quay_image_name = image_name.replace("docker.io", "quay.io").replace("swebench/", "vllm/swebench:").split(":latest")[0]
    if image_exists_on_hub(quay_image_name):
        print(f"{quay_image_name} exists")
        continue
    print(f"docker image pull {image_name}")
    image = client.images.pull(image_name, tag='latest')
    time.sleep(random.randint(3, 17))
    print(f"docker image tag {image_name} {quay_image_name}")
    tagged = image.tag(quay_image_name, force= True)
    print(f"docker image push {quay_image_name}")
    client.images.push(quay_image_name )
    print(f"Push complete: {quay_image_name}")


