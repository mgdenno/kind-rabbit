# KIND RABBIT 
This repository provides a simple example of using RabbitMQ in Kubernetes to run jobs in parallel in separate containers.  In reality you will probably run this on a remote cloud cluster, but for development and testing running in Kind is convenient.

# Prerequisites
## Install kubectl
`kubectl` is a command line interface to interact with kubernetes clusters.
https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

## Install KIND
Kind is "Kubernetes in Docker" is a tool for running local Kubernetes clusters using Docker container “nodes”.  It is primarily used for development and testing and not production work loads.
https://kind.sigs.k8s.io/docs/user/quick-start/#installation

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.11.1/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr.local/bin/kind

kind create cluster
kubectl cluster-info --context kind-kind
```

## Install k9s
We will use k9s to monitor and initeract with the running cluster.
https://github.com/derailed/k9s


# To Use
First delete any existing Kind clusters, then create a new one using the provided script.  This creates a new cluster and also sets up a local repository to use for Docker images.
```bash
# delete any existing clusters
kind delete cluster

# create new cluster and image registry
./kind/create_cluster.sh

# check cluster status
kubectl cluster-info --context kind-kind

# check that there are 2 containers running, kindest/node:v1.21.1 and registry:2
docker ps
```

There are three containers that are used in this example.
- RabbitMQ - We use a prebuilt image from docker for that runs the queue.  This image gets applied to the cluster from the local repository that we created with `create_cluster.sh`.
- Worker - This is an image that we build based on a Python base image that takes tasks from the queue and executes them.  This image gets spun up to "do the work" as part of a deployment.
- Creator - This is an image that we build based on a Python base image that creates jobs and adds them to the queue.  In a real system you would likely have a different mechanism for adding jobs to the queue.

We will use the provided docker-compose.yml file to build the `creator` and `worker` containers and push them to the local registry.  This will build the Dockerfile in the `creator` and `worker` directories and push them to the container registry where the cluster will pull them from when needed.

```bash
docker-compose build
docker-compose push
```
Now that the containers we need to use are in the registry, we can apply the configurations to the cluster so that the cluster will create/run them.  It is probably a good idea to start `k9s` now in a separate terminal so that you can monitor the cluster as we apply configurations and run commands against it.  First apply the `rabbit.yaml` files to add RabbitMQ to the cluster.
```bash
kubectl apply -f k8s/rabbit.yaml
```
You should see a rabbit pod running in the cluster now in `k9s`.  Next, apply the `creator_job.yaml` file.  This will create a a bunch of sample jobs and add them to the queue.
```bash
kubectl apply -f k8s/creator_job.yaml
```
Now, in `k9s` if you select the `creator-job-xxx` pod and hit "l" it will show you the logs which indicate the jobs were added to the queue.  They will just sit there until a worker takes them and acts on them.

In `k9s` you can also forward the RabbitMQ port to the localhost (shift-f) and see the queue via the web http://localhost:15672/, user: admin, password: queue

Lastly, as far as adding jobs to the queue is concerned, you can also port forward port 5672 to localhost and add jobs to the queue by running the creator/creator.py script locally.  You just need to change the rabbit host from rabbit-queue to localhost, as noted in the file.

Now we need to create worker deployments to do the work (of "running the model", which in this case is really just waiting a random amount of time.)

First we need to install a Python virtual environment.
```bash
pipenv install
pipenv shell
```

Once installed you can run the create_worker_deployments.py script to create worker pods, that will take jobs from the queue, execute them, and acknowledge that they are done. The script takes some command line arguments to create, delete, update and restart the deployment of worker pods.

To create the deployments:
```bash
python create_workers_deployments.py --create
```

To delete the deployments:
```bash
python create_workers_deployments.py --delete
```

To remove remove the cluster and delete all the pods, containers, etc.
```bash
kind delete cluster
```