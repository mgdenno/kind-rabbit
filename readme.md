# Install kubectl
https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

# Install KIND
https://kind.sigs.k8s.io/docs/user/quick-start/#installation

curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.11.1/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr.local/bin/kind

kind create cluster
kubectl cluster-info --context kind-kind

# Install k9s
https://github.com/derailed/k9s

clear

add line to file, and another

