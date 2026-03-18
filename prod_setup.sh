#!/bin/bash

INVENTORY="hosts"
TARGET="/etc/playbook/hosts"

if [ ! -f "$INVENTORY" ]; then
  echo "Error: $INVENTORY not found!"
  exit 1
fi

if [ ! -f ~/.ssh/id_rsa ]; then
  echo "Creating local SSH key..."
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
fi

if [ -f "$TARGET" ]; then
  echo "Inventory already exists at $TARGET. Using existing system file."
  SELECTED_HOSTS_FILE="$TARGET"
else
  echo "Inventory not found at $TARGET. Deploying local $INVENTORY..."
  if [ ! -f "$INVENTORY" ]; then
    echo "Error: Local $INVENTORY not found to deploy!"
    exit 1
  fi
  sudo mkdir -p /etc/playbook
  sudo cp "$INVENTORY" "$TARGET"
  sudo chown $USER "$TARGET"
  SELECTED_HOSTS_FILE="$TARGET"
fi

mapfile -t all_hosts < <(grep -v -E '^\[|^#|^$' "$SELECTED_HOSTS_FILE")

echo "Authorizing keys on all servers found in $SELECTED_HOSTS_FILE"

for host in "${all_hosts[@]}"; do
  host=$(echo "$host" | xargs)
  if [ -n "$host" ]; then
    echo "Processing $host..."
    ssh-copy-id -o ConnectTimeout=5 -i ~/.ssh/id_rsa.pub "$USER@$host"
  fi
done

echo "Done!"
