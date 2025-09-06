# ✅ **EC2 Deployment Checklist**

## **Pre-Deployment**
- [ ] EC2 instance launched (Ubuntu 22.04 LTS)
- [ ] Security group configured (ports 22, 80, 8001)
- [ ] SSH key pair downloaded
- [ ] Can connect to EC2 via SSH

## **File Upload**
- [ ] Files uploaded to EC2 (via SCP or Git)
- [ ] Files moved to `/opt/ethanol_analyzer/`
- [ ] Correct file permissions set (`chown ubuntu:ubuntu`)

## **Installation**
- [ ] Python 3 and pip installed
- [ ] Virtual environment created
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] Deploy script executed (`./deploy.sh`)

## **Service Setup**
- [ ] Systemd service created and enabled
- [ ] Service started successfully
- [ ] Service status: Active (running)

## **Testing**
- [ ] Health check works: `curl http://localhost:8001/api/health`
- [ ] Frontend accessible: `http://your-ec2-ip:8001`
- [ ] External access works from browser
- [ ] Can enter Gemini API key and analyze vehicles

## **Final Steps**
- [ ] Document your EC2 public IP
- [ ] Share access URL with users
- [ ] Monitor logs: `sudo journalctl -u ethanol-analyzer -f`

---

## **Quick Deploy Commands**

```bash
# 1. Upload to EC2
scp -i your-key.pem -r ethanol_analyzer ubuntu@your-ec2-ip:~/

# 2. Connect and setup
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo mv ethanol_analyzer /opt/
sudo chown -R ubuntu:ubuntu /opt/ethanol_analyzer
cd /opt/ethanol_analyzer

# 3. Deploy
chmod +x deploy.sh
./deploy.sh

# 4. Verify
curl http://localhost:8001/api/health
```

## **Success Indicators**
✅ Service status shows "Active (running)"
✅ Health endpoint returns JSON response
✅ Frontend loads in browser at `http://your-ec2-ip:8001`
✅ Can submit analysis requests with Gemini API key

## **Common Issues & Solutions**

**"Connection refused" when accessing from browser:**
- Check security group allows inbound port 8001
- Verify service is running: `sudo systemctl status ethanol-analyzer`

**"Address already in use" error:**
- Kill existing process: `sudo pkill -f uvicorn`
- Restart service: `sudo systemctl restart ethanol-analyzer`

**Python package errors:**
- Activate virtual environment: `source /opt/ethanol_analyzer/ethanol_env/bin/activate`
- Reinstall packages: `pip install -r requirements.txt`