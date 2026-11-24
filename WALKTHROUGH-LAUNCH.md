# Run and package Webcam Studio, line by line

Python runs the web server and the vision models. The Node.js command starts that server in development and the Node.js test runner checks the browser's shared coordinate helpers. The container runs the same Python process on Linux. These entry points meet at [web_server.py](web_server.py).

## Node.js launch flow

Running npm start calls [scripts/studio.mjs](scripts/studio.mjs). Node reads the selected app slug, determines which Python executable to use, and launches the server with its terminal attached. Ctrl+C reaches the Python child so active socket sessions can close. The selected slug changes the URL printed in the terminal. App selection itself happens when the browser loads that URL.

## `package.json`

- **1** Open the package metadata object that npm reads.
- **2** Give the Node project its local name.
- **3** Make this an application repository and prevent accidental publication to the npm registry.
- **4** Treat the JavaScript files as standard ECMAScript modules.
- **5** State the minimum Node.js version used by the launcher and the test runner.
- **6** Start the npm command definitions.
- **7** Run the Node launcher from npm start.
- **8** Check browser JavaScript syntax, then run the mirror coordinate tests with Node.
- **9** End the command definitions.
- **10** End the package file.

## `scripts/studio.mjs`

- **1** Import the built-in function that starts a Python process without a shell.
- **2** Import the filesystem check for the virtual environment's Python.
- **3** Import the conversion between file URLs and native paths.
- **5** Find the project root relative to this script, regardless of where the user called it.
- **6** List the four routes that the Node command can suggest.
- **7** Read the first argument as the mode and collect any extras for validation.
- **8** Pick the standard Python path for Windows or other platforms.
- **9** Use a configured Python command when present or resolve the project's environment by default.
- **11** Check for too many arguments or an unknown route.
- **12** Print the valid mode names so the user can correct the command.
- **13** Set the command's exit code to indicate invalid arguments.
- **14** Detect a missing default Python environment before starting the server.
- **15** Point to the installation instructions.
- **16** Report setup failure through the exit status.
- **17** Proceed only when argument and environment checks pass.
- **18** Print the localhost URL with the selected mode, when provided.
- **19** Start the same Python web server used by the direct Python command and show its output in the terminal.
- **20** Forward Ctrl+C or termination to that child process.
- **21** Register a callback for operating system errors starting the child.
- **22** Print the error description for troubleshooting.
- **23** Set an unsuccessful exit status if Python could not start.
- **24** Finish the startup-error callback.
- **25** Register a callback for the Python server exiting.
- **26** Propagate Python's exit status. Treat the normal stop signals as a successful close when a numeric code is absent.
- **27** Finish the exit callback.
- **28** End the launch branch.

## `Dockerfile`

- **1** Use a Debian-based CPython 3.12 image that accepts the pinned Linux wheels.
- **3** Set the working directory for dependency installation and app startup.
- **4** Install certificates and shared libraries, including EGL and OpenGL ES, needed by the native Linux vision packages.
- **5** Remove package-index data after installing the libraries to reduce the final image size.
- **6** Copy the package pins first so Docker can reuse the dependency layer when app code changes.
- **7** Install Python dependencies into the image without leaving pip's download cache.
- **8** Copy the Python code used by the desktop and web modes and the unit tests.
- **9** Copy the single browser interface.
- **10** Download the pinned models during the build and verify their hashes. Container startup can then use the included weights.
- **12** Provide a default HTTP port that a hosting service can override.
- **13** Document the default port at the image level.
- **14** Start Uvicorn on all container interfaces, apply the same WebSocket limits as the local server, and replace the shell process so stop signals reach Uvicorn.

## `.dockerignore`

- **1** Exclude Git history from the files Docker receives.
- **2** Exclude the local Python environment. The image installs the Linux packages itself.
- **3** Exclude generated Python bytecode.
- **4** Exclude locally cached weights. The Docker build obtains the files from the pinned manifest.
- **5** Exclude local Node dependencies. The container serves the browser source files directly.

## `.github/workflows/check.yml`

- **1** Name the release checks for GitHub's Actions page.
- **3** Run the checks on pushed changes and proposed merges.
- **5** Begin the minimum access settings for the runner.
- **6** Allow the runner to read source files.
- **8** Start the jobs for this workflow.
- **9** Define one job that validates both languages and builds the image.
- **10** Use a Linux virtual machine with Docker.
- **11** Start the ordered steps in the job.
- **12** Check out the exact source revision being checked.
- **13** Install the Node.js runtime used by the project.
- **14** Supply the runtime selector to that action.
- **15** Use Node.js 22, the supported version declared by npm.
- **16** Check browser syntax and run the coordinate tests.
- **17** Build the Linux image, including dependency install and model checksum verification.
- **18** Run the Python tests inside that same image.
- **19** Start a shell step that checks the running container.
- **20** Start a container and bind its port to the runner's loopback interface.
- **21** Stop that container when the check finishes.
- **22** Retry the initial HTTP request until the server begins accepting connections and the object app route responds.
- **23** Run a Python WebSocket smoke test inside the started image.
- **24** Import JSON parsing to read the server's replies.
- **25** Import OpenCV to encode a generated image.
- **26** Import NumPy to allocate the image.
- **27** Import the synchronous WebSocket test client.
- **28** Name the object and gesture routes and the output fields they should return.
- **29** Add the corresponding caption and silhouette checks.
- **30** Encode a small, uniform image as a JPEG without using a webcam.
- **31** Run the same exchange once for each app mode.
- **32** Open the live WebSocket with the corresponding same-origin header.
- **33** Wait for the real session and model setup to acknowledge readiness.
- **34** Send the generated JPEG through the same input path as the website.
- **35** Read the response produced by the native Linux pipeline.
- **36** Check that processing succeeded and produced the expected field.
- **37** Print the mode that passed so failures point to a specific pipeline.
- **38** End the Python program embedded in this check.

The public portfolio deployment routes are separate from this local launcher. See [the web server guide](WALKTHROUGH-SERVER.md) for how the HTTP page and WebSocket endpoint meet the Python processors.
