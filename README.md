# Deepfake Detection

Major project on detecting face swaps and deepfakes using Python and machine learning libraries.

---

## 🔧 Setup Instructions

### 1. Clone the repository (if applicable)
```bash
git clone https://github.com/cgdhanush/deepfake
```
### 2. Create a Conda Environment

```
conda create --name deepfake python=3.11 -y
conda activate deepfake
```

### 3. Install Dependencies

````
pip install -r deepfake/requirements.txt
````

### 3. Create User Directory

````
mkdir user_data 
````

### 3. Create config.json inside user_data and paste this

````
{
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 5000,
        "verbosity": "error",
        "enable_openapi": false,
        "CORS_origins": []
        
    }
}
````

#### then save the file go to parent dir and run the following command


---


## 🚀 Run the Project

```
python -m deepfake start
```