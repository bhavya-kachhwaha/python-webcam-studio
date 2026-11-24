# Model setup, line by line

The AI apps read their model files from the `models` directory. The downloader fetches fixed model versions and checks their SHA-256 digests before publishing them at the paths the apps expect. It reads model files and makes HTTP requests to the listed model hosts. It does not open the webcam. Open [download_models.py](download_models.py) alongside the guide.

## `download_models.py`

### Imports and download manifest

- **1** Imports `argparse` for selecting an app from the command line.
- **2** Imports `hashlib` for computing the SHA-256 digest of a file.
- **3** Imports `Path` to work with file and directory paths.
- **4** Imports `NamedTemporaryFile` so incomplete downloads can stay separate from installed models.
- **5** Imports `urlopen` to read a model from its HTTPS address.
- **7** Imports the common model directory and the function that handles errors and terminal interrupts.
- **10** Stores the base address of Google's official MediaPipe model files.
- **11** Stores the caption model's base address, including the exact Hugging Face revision identifier after `resolve/`.
- **12** Starts the manifest. Each app name maps to one or more entries containing a relative path, a URL, and a checksum.
- **13** Starts the entry list for named object detection.
- **14** Specifies the local filename and exact remote address of EfficientDet-Lite2.
- **15** Specifies the expected SHA-256 checksum for that model.
- **16** Ends the object detector's entry list.
- **17** Starts the entry list for gesture recognition.
- **18** Specifies the filename and fixed MediaPipe download address for the gesture recognizer bundle.
- **19** Specifies the expected checksum for the gesture recognizer bundle.
- **20** Ends the gesture recognizer's entry list.
- **21** Starts the entry list for the particle silhouette.
- **22** Specifies the filename and exact address for the landscape selfie segmentation model.
- **23** Specifies the expected checksum for the segmentation model.
- **24** Ends the segmentation model's entry list.
- **25** Starts the caption model's entry list. It has several files because tokenization, image encoding, and word generation are handled separately.
- **26** Specifies the tokenizer's local path and remote address. The tokenizer translates between caption text and numeric token IDs.
- **27** Specifies the tokenizer checksum.
- **28** Specifies the image encoder path and remote address. The `quantized` model uses reduced-precision weights to keep the download and runtime smaller.
- **29** Specifies the encoder checksum.
- **30** Specifies the quantized text decoder path and remote address. The decoder predicts word pieces from the image features and tokens it has already produced.
- **31** Specifies the decoder checksum.
- **32** Ends the caption assets' entry list.
- **33** Closes the manifest dictionary.

### Verify and install one file

- **36** Defines `download` with the local filename, remote URL, and expected hash as inputs.
- **37** Joins the local filename to the project's model directory. This also supports paths with subfolders such as `caption/onnx`.
- **38** Checks whether the destination already exists as a file.
- **39** Opens an existing file in binary mode so its digest uses the raw bytes.
- **40** Computes its SHA-256 digest and compares its hexadecimal representation to the expected string. A match lets the app reuse the installed file.
- **41** Reports the successful verification immediately, even when terminal output is buffered.
- **42** Returns early so the valid file stays in place.
- **44** Reports that a missing or mismatched asset will be downloaded.
- **45** Creates the destination directory and any needed parents. `exist_ok=True` accepts an already present directory.
- **46** Creates a temporary file in the destination directory. That location allows the final move to replace the destination in one operation on the same filesystem.
- **47** Converts the temporary file's name to a `Path` so the script can replace and remove files with the same API.
- **48** Begins a block that cleans up the temporary download even when something fails after creation.
- **49** Starts a running SHA-256 digest for the remote file.
- **50** Opens the HTTP response with a 60-second timeout on blocking network operations. The response closes when the block exits.
- **51** Reads up to 1 MiB at a time and assigns the bytes to `chunk`. The loop ends when the read returns no bytes.
- **52** Writes the current chunk to the temporary file.
- **53** Updates the running digest with the same bytes. This avoids a separate pass over the new file.
- **54** Compares the completed download's digest to the manifest value.
- **55** Reports a checksum mismatch and stops before the downloaded file reaches its final path.
- **56** Closes the temporary file so its buffered bytes are written and the file is ready to move.
- **57** Moves the verified file into place, replacing an existing copy if there was one.
- **58** Begins the cleanup block that runs on success or failure.
- **59** Removes the temporary file if it still exists. After a successful replacement, the temporary path is already gone.
- **60** Reports a successful download and verification.

### Select which assets to install

- **63** Defines the download script's entry point.
- **64** Builds the argument parser and gives `--help` a short description.
- **65** Defines an optional `project` argument. `nargs="?"` allows it to be omitted. The valid choices are `all` and the project names in the manifest.
- **66** Reads and validates the command-line options.
- **67** Selects every manifest key when the caller requests `all`. Otherwise it creates a one-item tuple containing the chosen project.
- **68** Goes through the selected project names.
- **69** Unpacks each project's asset entries into a filename, URL, and checksum.
- **70** Verifies or downloads each selected file.
- **73** Runs the script entry point when the user executes the file directly. Importing the functions leaves the network untouched.
- **74** Runs `main` through the shared error handler and returns the resulting exit status to the shell.

## `requirements.txt`

- **1** Pins the desktop OpenCV distribution with extra modules, which MediaPipe also requires. The apps use its camera, image processing, and native window APIs.
- **2** Pins MediaPipe Tasks, which runs the models for named objects, hand gestures, and person segmentation.
- **3** Pins ONNX Runtime, the inference engine that runs the image encoder and text decoder for captions.
- **4** Pins Tokenizers, which decodes the caption model's numeric token IDs into text.
- **5** Pins Pillow, which reads JPEG dimensions before decoding the browser's sampled frames.
- **6** Pins FastAPI, which serves the shared page and the WebSocket endpoint.
- **7** Pins Uvicorn, which runs the FastAPI application on localhost.
- **8** Pins the WebSocket protocol library used by the server.
- **9** Pins the HTTP client used to test WebSocket connections in-process.
