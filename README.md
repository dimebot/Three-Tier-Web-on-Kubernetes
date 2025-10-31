# Three-Tier Web Application on Kubernetes with Splunk Monitoring

This repository demonstrates a **Three-Tier Web Application** deployed on **Kubernetes**, monitored using **Splunk** with **Fluentd log forwarding**.

The setup consists of:
- **Frontend:** Nginx  
- **Backend:** Flask (Python)  
- **Database:** MySQL  
- **Monitoring:** Splunk (local container) + Fluentd via Splunk Connect for Kubernetes (Helm)
---
## Prerequisites

Ensure the following are installed:

- [Docker](https://www.docker.com/)
- [Minikube](https://minikube.sigs.k8s.io/docs/) or any other Kubernetes Cluster Environment.
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/)
- [Splunk Docker image](https://hub.docker.com/r/splunk/splunk)
---
## Installation
```bash
git clone https://github.com/dimebot/Three-Tier-Web-on-Kubernetes-with-Splunk-Monitoring.git
```
---
##  Deployment Steps
### 1. Start Minikube
```bash
minikube start
```
<br>

### 2. Create Kubernetes Secrets
Set the secrets as per your convenience, however make sure that **MYSQL_DATABASE**, **MYSQL_USER** and **MYSQL_PASSWORD** match in both Flask and MySQL secrets.

#### MySQL Secrets
```
kubectl create secret generic mysql-secrets \
  --from-literal=MYSQL_ROOT_PASSWORD=<root-password> \
  --from-literal=MYSQL_DATABASE=<database name> \
  --from-literal=MYSQL_USER=<username> \
  --from-literal=MYSQL_PASSWORD=<password>
  ```

#### Flask Secrets
```
kubectl create secret generic flask-secrets \
  --from-literal=MYSQL_USER=<username> \
  --from-literal=MYSQL_PASSWORD=<password> \
  --from-literal=MYSQL_HOST=<database name>
  ```

<br>

### 3. Spin up the Splunk Container
- Create a `.env` file and set the variable `SPLUNK_PASSWORD`.
- Start the container 
```
docker compose -f docker-compose.yml up -d
```
- Wait ~1 minute for the container to fully start.

<br>

### 4. Generate HEC token
-   Log in to Splunk Web (`http://<localhost>:8000`) 
-   Go to **Settings → Data Inputs → HTTP Event Collector → + Add New**
-   Enter a name (for example, `k8s-fluentd`)
-   Choose source type `_json`(optional)
-   Select an index (`main`),
-   Ensure the input is enabled
-   Click **Next** and **Finish**
-   Copy the generated **Token Value**
    
-   Use this token in your `enc_values.yaml`.
-  Also update the *host* in `enc_values.yaml`
**Note**: *The host name shouldn't be set to localhost, use your device's private IP retrieved from `ipconfig` or `ifconfig`*.

<br>

### 5. Deploy the Fluentd Daemonset using Helm
 ```
 helm install splunk-connect splunk/splunk-connect-for-kubernetes -f enc_values.yaml
 ```

<br>

 ### 6. Deploy the Web App
```
kubectl apply -f k8s/
```

<br>

 ### 6. Access the Web Application
 
Get the service URL:

```
minikube service nginx-frontend --url
```

Open the URL in your browser to access the frontend.

---

## Viewing Logs in Splunk

1.  Open Splunk Web → `http://localhost:8000`
    
2.  Go to **Search & Reporting**
    
3.  Run a search query such as:
    `index="main"` 
	- Set preset to **All time** if no log appears. 

----------

## Troubleshooting

-   **Splunk not receiving logs**
    
    -   Ensure HEC is enabled in Splunk (`Settings → Data Inputs → HTTP Event Collector`)
        
    -   Verify HEC token matches `token` in `enc_values.yaml`
        
    -   Check Fluentd pod logs for errors
        
-   **Pods in CrashLoopBackOff?**
    
    ```
    kubectl describe pod <pod-name>
    ```
    ```
    kubectl logs <pod-name>
    ```
    
-   **Access issues on localhost?**
    
    -   Use `minikube service nginx-frontend --url` to get the correct external URL.
## Author

**Shivam**  
🔗 [GitHub: @dimebot](https://github.com/dimebot)

----------

##  License

This project is licensed under the MIT License.

---
