# Security and private data

Jupyter access permits code execution as its Windows user. Keep it on loopback with authentication, and reach it through the existing SSH tunnel. A token is not a substitute for a narrow network boundary.

Do not include real usernames, device names, IP addresses, host-key fingerprints, public or private keys, tokens, recovery keys, or screenshots of connection details in contributions. Even public keys and private-network addresses are unnecessary identifying information here. Use placeholders.

Private configuration, task manifests, Jupyter runtime JSON, logs, and checkpoints belong under `.local/`, outside Git. Restrict that directory to the owner, SYSTEM, and Administrators before starting the helpers. Local administrators retain control over the machine; this setup does not isolate mutually untrusted administrators.

Review the staged diff and commit history before publishing. `.gitignore` is not a secret scanner and does not untrack existing files. Never print tokens in diagnostic reports. If credentials are accidentally published, revoke them promptly; deleting the visible file alone does not remove historical access.

For a vulnerability, use GitHub private vulnerability reporting if available. Otherwise contact the maintainer privately before publishing exploit details or real access material. Public issues should use minimal synthetic reproductions.
