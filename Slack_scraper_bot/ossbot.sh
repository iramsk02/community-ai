#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error occurred in command: $1"
    echo "Exiting script..."
    exit 1
}

# 1. Install GaiaNet Node
#echo "Step 1/4: Installing GaiaNet Node..."
curl -sSfL 'https://github.com/GaiaNet-AI/gaianet-node/releases/latest/download/install.sh' | bash || handle_error "Installation"

# 2. Source bashrc to make gaianet CLI available
#echo "Step 2/4: Sourcing ~/.bashrc to make gaianet CLI available..."
source ~/.bashrc || handle_error "Sourcing bashrc"

# 3. Initialize GaiaNet Node with specific configuration
echo "Step 3/4: Initializing GaiaNet Node with configuration..."
gaianet init --config https://raw.githubusercontent.com/GaiaNet-AI/node-configs/main/llama-3-8b-instruct/config.json \
--snapshot https://huggingface.co/datasets/FiendHunter/mifos_slack/resolve/main/default-6575143670696965-2025-03-27-21-43-37.snapshot \
--system-prompt "You are an expert agent" \
--rag-prompt "You are a slack bot that will help user resolve queries related to the slack channel."

# 4. Start GaiaNet Node in local-only mode
echo "Step 4/4: Starting GaiaNet Node in local-only mode..."
gaianet start --local-only || handle_error "Starting service"

echo "GaiaNet Node setup and startup completed successfully!"