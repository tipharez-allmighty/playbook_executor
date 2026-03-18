echo "Preparing to set up /etc/playbook/hosts..."

if [ ! -f ~/.ssh/id_rsa ]; then
  echo "Generating SSH key..."
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
else
  echo "SSH key already exists, skipping generation."
fi

echo "Authorizing keys..."
mkdir -p ~/.ssh
touch ~/.ssh/authorized_keys
if ! grep -q "$(cat ~/.ssh/id_rsa.pub)" ~/.ssh/authorized_keys; then
  cat ~/.ssh/id_rsa.pub >>~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
fi

read -p "Do you want to create a default local hosts file for testing (If hosts file already exist it will be overwritten? (y/n): " choice

if [[ "$choice" == [Yy]* ]]; then
  echo "Creating directory (may ask for your local password)..."
  sudo mkdir -p /etc/playbook
  sudo chown $USER /etc/playbook

  sudo bash -c "cat <<EOF > /etc/playbook/hosts
[webservers]
localhost
127.0.0.1
[dbservers]
127.0.0.1
localhost
EOF"
  echo "Default local hosts file created at /etc/playbook/hosts."
else
  echo "Skipped. Make sure you manually create and edit /etc/playbook/hosts before running the Python script."
fi

echo "Setup complete! You can run python script now."
