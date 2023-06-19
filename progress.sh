#!/bin/bash

total_iterations=100
progress_bar_width=50

# Function to draw the progress bar
draw_progress_bar() {
  local progress=$1
  local bar_length=$((progress * progress_bar_width / total_iterations))
  local bar=$(printf "%${bar_length}s" | tr ' ' '#')
  local spaces=$(printf "%$((progress_bar_width - bar_length))s")
  printf "\033[1;${progress_bar_width}H[%s%s] %d%%" "$bar" "$spaces" "$((progress * 100 / total_iterations))"
}

# Hide the cursor
tput civis

# Save the cursor position
tput sc

# Continuous progress bar at the bottom
for ((i = 1; i <= total_iterations; i++)); do
  # Perform your tasks here

  # Restore the saved cursor position
  tput rc

  # Clear the line
  tput el

  # Update the progress bar
  draw_progress_bar "$i"

  # Sleep for a short duration
  sleep 0.1
done

# Show the cursor
tput cnorm

# Print a new line after the loop
echo

