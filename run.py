import os
import sys
import time
import subprocess


def get_session_prefix(name, service):
    """Get the tmux session prefix based on tool name and service."""
    service_map = {
        "fdic": "1",
        "genome-nexus": "2",
        "language-tool": "3",
        "ocvn": "4",
        "ohsome": "5",
        "omdb": "6",
        "rest-countries": "7",
        "spotify": "8",
        "youtube": "9"
    }
    
    tool_prefix_map = {
        "evomaster": "evo",
        "resttestgen": "rtg",
        "schemathesis": "schema",
        "tcases": "tcases",
        "arat-rl": "arat",
        "arat-nlp": "arat",
        "llamaresttest": "llama",
        "llamaresttest-ex": "llama",
        "llamaresttest-ipd": "llama"
    }
    
    prefix = tool_prefix_map.get(name, "")
    service_num = service_map.get(service, "")
    return f"{prefix}{service_num}" if prefix and service_num else None


def launch_tool_docker(name, service, run_num, run_results_dir, base_dir):
    """Launch the tool in a Docker container for a specific run."""
    container_name = f"llamaresttest-run{run_num}"
    
    # Get absolute paths for volume mounting
    abs_base_dir = os.path.abspath(base_dir)
    abs_results_dir = os.path.abspath(run_results_dir)
    abs_models_dir = os.path.abspath(os.path.join(base_dir, "models"))
    
    # Ensure models directory exists
    os.makedirs(abs_models_dir, exist_ok=True)
    
    # Get Docker image name from docker-compose (format: <project>_<service>)
    # Default to common naming convention
    project_name = os.path.basename(os.path.abspath(base_dir)).lower().replace("-", "_")
    image_name = f"{project_name}_llamaresttest"
    
    # Try to get actual image name from docker-compose
    try:
        result = subprocess.run(["docker-compose", "config", "--images"], 
                              capture_output=True, text=True, cwd=base_dir)
        if "llamaresttest" in result.stdout:
            # Extract image name from output
            for line in result.stdout.split('\n'):
                if 'llamaresttest' in line and ':' in line:
                    image_name = line.split(':')[0].strip()
                    break
    except:
        pass  # Use default if we can't determine
    
    # Build docker run command
    # Note: Services should be started separately and shared via network
    docker_cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", "llamaresttest-network",
        "-v", f"{abs_models_dir}:/app/models:ro",
        "-v", f"{abs_results_dir}:/app/results/run_{run_num}",
        "-v", f"{abs_base_dir}:/app",
        "-e", f"RUN_NUM={run_num}",
        "-e", f"RESULTS_DIR=/app/results/run_{run_num}",
        "-e", "PYTHONPATH=/app",
        "-e", "JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64",
        "--rm",  # Auto-remove container when it stops
        image_name,
        "bash", "-c",
        # Services are assumed to be running, just run the tool
        f"cd /app && source venv/bin/activate && python run.py {name} {service}"
    ]
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Error launching Docker container for run {run_num}: {e.stderr}")
        return None


def launch_tool(name, service, run_num, run_results_dir, env):
    """Launch the tool in a tmux session for a specific run."""
    session_prefix = get_session_prefix(name, service)
    if not session_prefix:
        print(f"Warning: Unknown tool/service combination: {name}/{service}")
        return None
    
    session_name = f"{session_prefix}_run{run_num}"
    
    # Build the command based on tool name and service
    if name == "evomaster":
        tool_paths = {
            "fdic": "tool/evomaster/fdic",
            "genome-nexus": "tool/evomaster/genome-nexus",
            "language-tool": "tool/evomaster/language-tool",
            "ocvn": "tool/evomaster/ocvn",
            "ohsome": "tool/evomaster/ohsome",
            "omdb": "tool/evomaster/omdb",
            "rest-countries": "tool/evomaster/rest-countries",
            "spotify": "tool/evomaster/spotify",
            "youtube": "tool/evomaster/youtube"
        }
        script_name = "./tool.sh"
    elif name == "resttestgen":
        tool_paths = {
            "fdic": "tool/resttestgen/fdic",
            "genome-nexus": "tool/resttestgen/genome-nexus",
            "language-tool": "tool/resttestgen/language-tool",
            "ocvn": "tool/resttestgen/ocvn",
            "ohsome": "tool/resttestgen/ohsome",
            "omdb": "tool/resttestgen/omdb",
            "rest-countries": "tool/resttestgen/rest-countries",
            "spotify": "tool/resttestgen/spotify",
            "youtube": "tool/resttestgen/youtube"
        }
        script_name = "./tool.sh"
    elif name == "schemathesis":
        tool_paths = {
            "fdic": "tool/schemathesis/fdic",
            "genome-nexus": "tool/schemathesis/genome-nexus",
            "language-tool": "tool/schemathesis/language-tool",
            "ocvn": "tool/schemathesis/ocvn",
            "ohsome": "tool/schemathesis/ohsome",
            "omdb": "tool/schemathesis/omdb",
            "rest-countries": "tool/schemathesis/rest-countries",
            "spotify": "tool/schemathesis/spotify",
            "youtube": "tool/schemathesis/youtube"
        }
        script_name = "./tool.sh"
    elif name == "tcases":
        tool_paths = {
            "fdic": "tool/tcases/fdic",
            "genome-nexus": "tool/tcases/genome-nexus",
            "language-tool": "tool/tcases/language-tool",
            "ocvn": "tool/tcases/ocvn",
            "ohsome": "tool/tcases/ohsome",
            "omdb": "tool/tcases/omdb",
            "rest-countries": "tool/tcases/rest-countries",
            "spotify": "tool/tcases/spotify",
            "youtube": "tool/tcases/youtube"
        }
        script_name = "tool.sh"
    elif name == "arat-rl":
        tool_paths = {
            "fdic": "tool/arat/fdic",
            "genome-nexus": "tool/arat/genome-nexus",
            "language-tool": "tool/arat/language-tool",
            "ocvn": "tool/arat/ocvn",
            "ohsome": "tool/arat/ohsome",
            "omdb": "tool/arat/omdb",
            "rest-countries": "tool/arat/rest-countries",
            "spotify": "tool/arat/spotify",
            "youtube": "tool/arat/youtube"
        }
        script_name = "tool.sh"
    elif name == "arat-nlp":
        tool_paths = {
            "fdic": "tool/arat/fdic-nlp",
            "genome-nexus": "tool/arat/genome-nexus-nlp",
            "language-tool": "tool/arat/language-tool-nlp",
            "ocvn": "tool/arat/ocvn-nlp",
            "ohsome": "tool/arat/ohsome-nlp",
            "omdb": "tool/arat/omdb-nlp",
            "rest-countries": "tool/arat/rest-countries-nlp",
            "spotify": "tool/arat/spotify-nlp",
            "youtube": "tool/arat/youtube-nlp"
        }
        script_name = "tool.sh"
    elif name == "llamaresttest":
        tool_paths = {
            "fdic": "tool/llama/fdic",
            "genome-nexus": "tool/llama/genome-nexus",
            "language-tool": "tool/llama/language-tool",
            "ocvn": "tool/llama/ocvn",
            "ohsome": "tool/llama/ohsome",
            "omdb": "tool/llama/omdb",
            "rest-countries": "tool/llama/rest-countries",
            "spotify": "tool/llama/spotify",
            "youtube": "tool/llama/youtube"
        }
        script_name = "tool.sh"
    elif name == "llamaresttest-ex":
        tool_paths = {
            "fdic": "tool/llama2/fdic",
            "genome-nexus": "tool/llama2/genome-nexus",
            "language-tool": "tool/llama2/language-tool",
            "ocvn": "tool/llama2/ocvn",
            "ohsome": "tool/llama2/ohsome",
            "omdb": "tool/llama2/omdb",
            "rest-countries": "tool/llama2/rest-countries",
            "spotify": "tool/llama2/spotify",
            "youtube": "tool/llama2/youtube"
        }
        script_name = "tool.sh"
    elif name == "llamaresttest-ipd":
        tool_paths = {
            "fdic": "tool/llama3/fdic",
            "genome-nexus": "tool/llama3/genome-nexus",
            "language-tool": "tool/llama3/language-tool",
            "ocvn": "tool/llama3/ocvn",
            "ohsome": "tool/llama3/ohsome",
            "omdb": "tool/llama3/omdb",
            "rest-countries": "tool/llama3/rest-countries",
            "spotify": "tool/llama3/spotify",
            "youtube": "tool/llama3/youtube"
        }
        script_name = "tool.sh"
    else:
        print(f"Warning: Unknown tool name: {name}")
        return None
    
    tool_path = tool_paths.get(service)
    if not tool_path:
        print(f"Warning: Unknown service: {service}")
        return None
    
    # Launch the tool in tmux
    cmd = f"tmux new -d -s {session_name} 'cd {tool_path} && RESULTS_DIR={run_results_dir} RUN_NUM={run_num} bash {script_name}'"
    subprocess.run(cmd, shell=True, env=env)
    return session_name


if __name__ == "__main__":
    name = sys.argv[1]
    service = sys.argv[2]
    
    # Ask user for number of runs
    num_runs = int(input("Enter the number of runs needed: "))
    
    # Ask if they want to run in parallel
    run_parallel = input("Run in parallel? (y/n, default: n): ").strip().lower() == 'y'
    
    # Ask if they want Docker isolation (only relevant for parallel runs)
    use_docker = False
    if run_parallel:
        use_docker = input("Use Docker containers for isolation? (y/n, default: y): ").strip().lower() != 'n'
    
    # Create results directory if it doesn't exist
    results_base_dir = "results"
    os.makedirs(results_base_dir, exist_ok=True)

    # Check if we're already in Docker
    in_docker = os.path.exists("/.dockerenv")
    
    # Start services (only if not using Docker for parallel runs)
    # If using Docker, services will be started in a shared container later
    # For sequential runs or parallel tmux runs, start services now
    should_start_services_now = (not run_parallel) or (run_parallel and not use_docker)
    
    if should_start_services_now and not in_docker:
        print("Starting services...")
        subprocess.run("cd services && python run_service.py all", shell=True)
        print("Waiting for services to be ready (300 seconds)...")
        time.sleep(300)
    
    current_path = os.getcwd()
    
    # Store container/session names for cleanup
    container_names = []
    session_names = []
    
    if run_parallel:
        # Launch all runs in parallel
        print(f"\n{'='*60}")
        if use_docker:
            print(f"Launching {num_runs} runs in PARALLEL (Docker containers)")
        else:
            print(f"Launching {num_runs} runs in PARALLEL (tmux sessions)")
        print(f"{'='*60}\n")
        
        # Setup Docker environment if using Docker
        if use_docker:
            # Check if we're in Docker (can't launch containers from inside)
            if in_docker:
                print("Warning: Cannot launch Docker containers from inside Docker.")
                print("Falling back to tmux sessions for parallel execution.")
                use_docker = False
            else:
                print("Setting up Docker environment...")
                # Ensure Docker network exists
                subprocess.run(["docker", "network", "create", "llamaresttest-network"], 
                             capture_output=True)  # Ignore error if network already exists
                
                # Build/ensure Docker image exists
                print("Ensuring Docker image is built...")
                subprocess.run(["docker-compose", "build"], capture_output=True)
                
                # Start shared services (MongoDB and main service container for shared services)
                print("Starting shared services...")
                subprocess.run(["docker-compose", "up", "-d", "gn-mongo"], capture_output=True)
                
                # Get Docker image name (same logic as launch_tool_docker)
                project_name = os.path.basename(os.path.abspath(current_path)).lower().replace("-", "_")
                image_name = f"{project_name}_llamaresttest"
                try:
                    result = subprocess.run(["docker-compose", "config", "--images"], 
                                          capture_output=True, text=True, cwd=current_path)
                    if "llamaresttest" in result.stdout:
                        for line in result.stdout.split('\n'):
                            if 'llamaresttest' in line and ':' in line:
                                image_name = line.split(':')[0].strip()
                                break
                except:
                    pass
                
                # Start services in a shared container (they'll be accessible via network)
                print("Starting services in shared container...")
                shared_container = "llamaresttest-services"
                # Check if container already exists
                result = subprocess.run(["docker", "ps", "-a", "--filter", f"name={shared_container}", "--format", "{{.Names}}"],
                                      capture_output=True, text=True)
                if shared_container not in result.stdout:
                    subprocess.run([
                        "docker", "run", "-d",
                        "--name", shared_container,
                        "--network", "llamaresttest-network",
                        "-v", f"{os.path.abspath(current_path)}:/app",
                        "-e", "PYTHONPATH=/app",
                        "-e", "JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64",
                        image_name,
                        "bash", "-c", "cd /app && source venv/bin/activate && cd services && python run_service.py all && tail -f /dev/null"
                    ], capture_output=True)
                else:
                    # Restart if exists but stopped
                    subprocess.run(["docker", "start", shared_container], capture_output=True)
                
                print("Waiting for services to be ready (300 seconds)...")
                time.sleep(300)
        
        for run_num in range(1, num_runs + 1):
            # Create run-specific results directory
            run_results_dir = os.path.join(results_base_dir, f"run_{run_num}")
            os.makedirs(run_results_dir, exist_ok=True)
            
            if use_docker:
                # Launch in Docker container
                container_name = launch_tool_docker(name, service, run_num, run_results_dir, current_path)
                if container_name:
                    container_names.append(container_name)
                    print(f"Started Run {run_num} (container: {container_name})")
            else:
                # Launch in tmux session
                env = os.environ.copy()
                env['RUN_NUM'] = str(run_num)
                env['RESULTS_DIR'] = run_results_dir
                
                session_name = launch_tool(name, service, run_num, run_results_dir, env)
                if session_name:
                    session_names.append(session_name)
                    print(f"Started Run {run_num} (session: {session_name})")
        
        # Wait for all runs to complete (3600 seconds = 1 hour)
        print(f"\nWaiting for all {num_runs} runs to complete (3600 seconds)...")
        if use_docker:
            print("All runs are executing in parallel Docker containers.\n")
        else:
            print("All runs are executing in parallel tmux sessions.\n")
        time.sleep(3600)
        
        # Clean up
        print(f"\nCleaning up...")
        if use_docker:
            for container_name in container_names:
                print(f"  Stopping container: {container_name}")
                subprocess.run(f"docker stop {container_name} 2>/dev/null", shell=True)
                subprocess.run(f"docker rm {container_name} 2>/dev/null", shell=True)
            # Optionally clean up shared services container (commented out to keep services running)
            # print("  Stopping shared services container...")
            # subprocess.run(["docker", "stop", "llamaresttest-services"], capture_output=True)
        else:
            for session_name in session_names:
                subprocess.run(f"tmux kill-session -t {session_name} 2>/dev/null", shell=True)
                print(f"  Killed session: {session_name}")
        
        print(f"\n{'='*60}")
        print(f"All {num_runs} parallel runs completed!")
        print(f"Results are stored in: {results_base_dir}/")
        print(f"{'='*60}\n")
    else:
        # Run sequentially (original behavior)
        for run_num in range(1, num_runs + 1):
            print(f"\n{'='*60}")
            print(f"Starting Run {run_num} of {num_runs}")
            print(f"{'='*60}\n")
            
            # Create run-specific results directory
            run_results_dir = os.path.join(results_base_dir, f"run_{run_num}")
            os.makedirs(run_results_dir, exist_ok=True)
            
            # Set environment variable for results directory (tools can use this)
            env = os.environ.copy()
            env['RUN_NUM'] = str(run_num)
            env['RESULTS_DIR'] = run_results_dir

            # Launch the tool
            session_name = launch_tool(name, service, run_num, run_results_dir, env)
            
            # Wait for the tool to complete (3600 seconds = 1 hour)
            print(f"Waiting for Run {run_num} to complete (3600 seconds)...")
            time.sleep(3600)
            
            # Kill tmux session for this run
            print(f"Cleaning up tmux session for Run {run_num}...")
            if session_name:
                subprocess.run(f"tmux kill-session -t {session_name} 2>/dev/null", shell=True)
            
            print(f"Run {run_num} completed. Results saved to {run_results_dir}\n")
        
        print(f"\n{'='*60}")
        print(f"All {num_runs} runs completed!")
        print(f"Results are stored in: {results_base_dir}/")
        print(f"{'='*60}\n")