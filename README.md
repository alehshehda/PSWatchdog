# PSWatchdog
## Implementation of a User Activity Monitoring System in PowerShell

### **Configuration of the Remote Server**
This guide provides step-by-step instructions for configuring a remote Ubuntu 24.04 server. The configuration sets up an SFTP jail for securely storing logs sent from users. All configurations should be performed while logged in as **root**.

---

### **1. Set a Static IP Address**
Edit the Netplan configuration file:
```bash
nano /etc/netplan/50-cloud-init.yaml
```
Modified file should look something like this(it will vary):
```yaml
network:
  version: 2
  wifis:
    wlan0:
      optional: true
      dhcp4: no  # Disable DHCP
      addresses:
        - 192.168.0.100/24  # Static IP address
      routes:
        - to: 0.0.0.0/0  # Default route
          via: 192.168.0.1  # Router gateway
      nameservers:
        addresses:
          - 8.8.8.8  # Google DNS
          - 1.1.1.1  # Cloudflare DNS
      access-points:
        "youraccesspoint":
          auth:
            key-management: "yourkeymanagement"
            password: "yourpassword"
```
Basically you only need to add:
```yaml
        - 192.168.0.100/24  # Static IP address
      routes:
        - to: 0.0.0.0/0  # Default route
          via: 192.168.0.1  # Router gateway
      nameservers:
        addresses:
          - 8.8.8.8  # Google DNS
          - 1.1.1.1  # Cloudflare DNS
```
Apply the new network configuration:
```bash
netplan apply
```
If the network does not restart properly, reboot the server:
```bash
systemctl reboot
```

---

### **2. Create the Logsink User**
This user will be responsible for receiving logs from clients.
```bash
adduser logsink  
```
Disable interactive login for the user:
```bash
usermod --shell /usr/sbin/nologin logsink
```
Verify the change:
```bash
grep logsink /etc/passwd
```
Expected output:
```
logsink:x:1004:1004::/home/logsink:/usr/sbin/nologin
```

---

### **3. Create a Dedicated Logs Directory**
Create a directory for storing logs and apply appropriate permissions:
```bash
mkdir -p /var/log/PSWatchdog  
chown root:logsink /var/log/PSWatchdog  
chmod 730 /var/log/PSWatchdog
```
Verify permissions:
```bash
ls -ld /var/log/PSWatchdog
```
Expected output:
```
drwx-wx--- 3 root logsink 4096 Mar 28 00:00 /var/log/PSWatchdog/
```

---

### **4. Configure SFTP Jail**
Create the jail directory and bind the logs directory to it:
```bash
mkdir -p /sftp-jail/var/log/PSWatchdog  
mount --bind /var/log/PSWatchdog /sftp-jail/var/log/PSWatchdog  
```
To make this binding persistent across reboots, edit **`/etc/fstab`**:
```bash
nano /etc/fstab  
```
Add the following line:
```
/var/log/PSWatchdog /sftp-jail/var/log/PSWatchdog none bind 0 0
```

---

### **5. Configure SSH for Secure SFTP Access**
Edit the SSH configuration file:
```bash
nano /etc/ssh/sshd_config  
```
Add the following settings at the end of the file:
```bash
# Restrict SFTP access for logsink user
Match User logsink  
    ForceCommand internal-sftp -u 0477  
    AuthorizedKeysFile /home/logsink/.ssh/authorized_keys  
    ChrootDirectory /sftp-jail/var/log  
    PasswordAuthentication no  
    PubkeyAuthentication yes  
    PermitTTY no  
    AllowTcpForwarding no  
    X11Forwarding no  
    MaxAuthTries 3  
```
Restart the SSH service to apply changes:
```bash
systemctl restart ssh
```

---

### **6. Create the authorized_keys File for SFTP Access**
The logsink user needs to authenticate using public key authentication. Create the `.ssh` directory and the `authorized_keys` file for the user:
```bash
mkdir -p /home/logsink/.ssh
touch /home/logsink/.ssh/authorized_keys
chown -R logsink:logsink /home/logsink/.ssh
chmod 700 /home/logsink/.ssh
chmod 600 /home/logsink/.ssh/authorized_keys
```
Now, the public keys of the client PCs must be stored in `/home/logsink/.ssh/authorized_keys`. You can copy the public key from each client and append it to this file:
```bash
cat /path/to/client/public/key >> /home/logsink/.ssh/authorized_keys
```
Ensure each public key is on a new line. This allows secure SSH key-based authentication for logsink users.

---

### **7. Verify SFTP Access from the Client PC**
Now, you should be able to log in using **SFTP** from the client machine:
```bash
sftp logsink@192.168.0.100
```
After connecting, verify that the logs directory is accessible:
```bash
ls -l
```
If configured correctly, the user **logsink** will only have access to `/var/log/PSWatchdog` through **SFTP**, without shell access, also has restricted access and can only put files into the remote user's directory.

---

## Setup Telegram Bot

**.env**
```sh
TELEGRAM_TOKEN=123:ABCD
TELEGRAM_CHAT_IDS=123456789,123456780
```
- Fill .env with **TELEGRAM_TOKEN**
- Go to [Telegram bot](http://t.me/PSWatchdog_bot) and write any message to the bot
- Run script and find ```chat': {'id': 123456789``` in stdout
- Fill **TELEGRAM_CHAT_IDS** (can use many chat ids separated by coma)