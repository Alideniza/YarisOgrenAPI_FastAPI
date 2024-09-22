import paramiko

def execute_command_on_server(hostname, username, password, command):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        ssh.connect(hostname, username=username, password=password)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Read the output
        print("Output:")
        for line in stdout:
            print(line.strip())
        
        # Read any errors
        print("Errors:")
        for line in stderr:
            print(line.strip())
    
    except Exception as e:
        print(f"Hata: {e}")
    
    finally:
        ssh.close()

if __name__ == "__main__":
    execute_command_on_server(
        hostname='5.180.185.145',
        username='yaris_user',
        password='Ogren2024*-+',
        command='ls -l'
    )
