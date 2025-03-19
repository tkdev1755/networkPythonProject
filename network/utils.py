import asyncio
import subprocess
import select
import sys
import time
import os

class NetworkEngine:

    def __init__(self):
        pass

    def launch_c_program(self,command, arguments=None):
        """Launches a C program and returns the process object.
        
        Args:
            command (str): Path to the C executable.
            arguments (list, optional): List of arguments to pass to the program.
        
        Returns:
            subprocess.Popen: Object representing the running process.
        """
        if arguments is None:
            arguments = []
        
        cmd_complete = [command] + arguments
        
        try :
            process = subprocess.Popen(
                cmd_complete,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                bufsize=0  # Non-buffered mode
            )
        except FileNotFoundError:
            print("Erreur : 'networkEngine' introuvable.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de 'networkEngine' : {e}")
                    
        # Configure streams in non-blocking mode
        os.set_blocking(process.stdout.fileno(), False)
        os.set_blocking(process.stderr.fileno(), False)
        
        return process
