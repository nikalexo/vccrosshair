#!/bin/bash

# Function to execute on each commit
process_commit() {
	    commit_hash=$1
	        # Replace this echo statement with your own custom logic
		    echo "Processing commit: $commit_hash"
		    vccrosshair --repo ../openssl --commit $commit_hash
		        # Add your function code here
		}
	# Colors
	red="\e[31m"
	green="\e[32m"
	blue="\e[34m"
	reset="\e[0m"
	
        # Print colored text
#	echo -e "${red}This text is red.${reset}"
#	echo -e "${green}This text is green.${reset}"
#	echo -e "${blue}This text is blue.${reset}"

        
	length=80
	character="-"
	separator=""
	for ((i=0; i<$length; i++))
	do
		separator="$separator$character"
	done
	
	echo "$separator"
	
        # Get the number of commit hashes as a command-line argument
	num_commits=$1

        # Print welcome message
	figlet "vccrosshair"
	echo "A tool developed in project ComPAss of ATHENE UCSP."

	echo "$separator"
	echo -e "Analyzing commits of project ${green}openssl${reset}"
	echo "$separator"
        # Validate the input
	if ! [[ $num_commits =~ ^[0-9]+$ ]]; then
		    echo "Error: Number of commits must be a positive integer."
		        exit 1
	fi

	# Get the specified number of commit hashes
	cd ../openssl
	commit_hashes=$(git log --oneline -n $num_commits --format="%H")

	# Iterate over each commit hash
	i=0
	for commit in $commit_hashes; do
		((i++))
		echo "Commit $i of $num_commits"
		process_commit $commit
		echo "$separator"
	done
	echo
