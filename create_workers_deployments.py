import datetime
import pytz
from kubernetes import client, config

import argparse

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Creates and destroys"
    )
    parser.add_argument(
        "--version", action="version",
        version = f"{parser.prog} version 0.1.0"
    )
    parser.add_argument(
        "--create", help="Create deployment", action='store_true'
    )
    parser.add_argument(
        "--delete", help="Delete deployment", action='store_true'
    )
    parser.add_argument(
        "--update", help="Update deployment", action='store_true'
    )
    parser.add_argument(
        "--restart", help="Restart deployment", action='store_true'
    )
    return parser

DEPLOYMENT_NAME = "worker-deployment"


def create_deployment_object():
    # Configure Pod template container
    # You can create multiple containers and add to pod spec.
    container = client.V1Container(
        name="worker",
        image="localhost:5001/worker",
        ports=[client.V1ContainerPort(container_port=80)],
        # resources=client.V1ResourceRequirements(
        #     requests={"cpu": "100m", "memory": "200Mi"},
        #     limits={"cpu": "500m", "memory": "500Mi"},
        # ),
    )

    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "worker"}),
        spec=client.V1PodSpec(containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=3, 
        template=template, 
        selector={
            "matchLabels":{"app": "worker"}
        }
    )

    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
        spec=spec,
    )

    return deployment


def create_deployment(api, deployment):
    # Create deployment
    resp = api.create_namespaced_deployment(
        body=deployment, namespace="default"
    )

    print("\n[INFO] deployment `worker-deployment` created.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )


def update_deployment(api, deployment):
    # Update container image
    deployment.spec.template.spec.containers[0].image = "localhost:5001/worker"

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )

    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )


def restart_deployment(api, deployment):
    # update `spec.template.metadata` section
    # to add `kubectl.kubernetes.io/restartedAt` annotation
    deployment.spec.template.metadata.annotations = {
        "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    }

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )

    print("\n[INFO] deployment `worker-deployment` restarted.\n")
    print("%s\t\t\t%s\t%s" % ("NAME", "REVISION", "RESTARTED-AT"))
    print(
        "%s\t%s\t\t%s\n"
        % (
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.metadata.annotations,
        )
    )


def delete_deployment(api):
    # Delete deployment
    resp = api.delete_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy="Foreground", grace_period_seconds=5
        ),
    )
    print("\n[INFO] deployment `worker-deployment` deleted.")


def main():
    parser = init_argparse()
    args = parser.parse_args()
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    # Uncomment the following lines to enable debug logging
    # c = client.Configuration()
    # c.debug = True
    # apps_v1 = client.AppsV1Api(api_client=client.ApiClient(configuration=c))

    # Create a deployment object with client-python API.

    deployment = create_deployment_object()
    if args.delete:
        delete_deployment(apps_v1)

    if args.create:
        create_deployment(apps_v1, deployment)
    
    if args.update:
        update_deployment(apps_v1, deployment)

    if args.restart:
        restart_deployment(apps_v1, deployment)



if __name__ == "__main__":
    main()