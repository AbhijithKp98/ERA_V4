# EC2 Deployment Instructions

## Prerequisites
- EC2 t2.nano instance with Amazon Linux
- Security Group configured
- SSH key pair

## Quick Deploy Commands

### 1. Connect to EC2
```bash
ssh -i "your-key.pem" ec2-user@YOUR_EC2_IP
```

### 2. Setup Environment
```bash
# Update packages
sudo yum update -y

# Install Python 3.8
sudo amazon-linux-extras install python3.8 -y

# Install pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install Git
sudo yum install git -y
```

### 3. Deploy Application
```bash
# Create app directory
mkdir ~/app && cd ~/app

# Copy your files here (use scp or create manually)
# main.py, requirements.txt, index.html

# Install dependencies
pip3 install fastapi uvicorn python-multipart

# Test run
python3 main.py
```

### 4. Configure Security Group
In AWS Console → EC2 → Security Groups:
- Add Inbound Rule: HTTP (80) from 0.0.0.0/0  
- Add Inbound Rule: Custom TCP (8000) from 0.0.0.0/0

### 5. Create Production Service
```bash
sudo tee /etc/systemd/system/animal-app.service > /dev/null <<EOF
[Unit]
Description=Animal Selector FastAPI App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/home/ec2-user/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable animal-app
sudo systemctl start animal-app
```

### 6. Access Your App
- Frontend: `http://YOUR_EC2_IP:8000` (served by FastAPI)
- API Docs: `http://YOUR_EC2_IP:8000/docs`

## File Structure on EC2
```
/home/ec2-user/app/
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies  
├── index.html          # Frontend
├── uploads/            # File upload directory (created automatically)
└── data.json          # Data storage (created automatically)
```

## Troubleshooting
```bash
# Check service status
sudo systemctl status animal-app

# View logs
sudo journalctl -u animal-app -f

# Restart service
sudo systemctl restart animal-app

# Check if port is listening
sudo netstat -tlnp | grep :8000
```

## Production Notes
- Consider using Nginx as reverse proxy for better performance
- Set up SSL certificate for HTTPS
- Configure firewall rules
- Set up monitoring and backups
- Use environment variables for configuration