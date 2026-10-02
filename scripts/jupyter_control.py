"""Inspect/stop this checkout's server. Only explicit 'token' prints a secret."""

import argparse
import json
import urllib.error
import urllib.request

from local_settings import LOCAL, load_settings


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(port, token, stop=False):
    endpoint = "shutdown" if stop else "contents"
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/{endpoint}",
        data=b"{}" if stop else None,
        headers={"Authorization": "token " + token, "Content-Type": "application/json"},
        method="POST" if stop else "GET",
    )
    # Never send a local token via a proxy or redirect.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(req, timeout=5) as response:
        return response.status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "stop", "token"))
    args = parser.parse_args()
    spec = load_settings()
    servers = []
    for path in (LOCAL / "runtime").glob("jpserver-*.json"):
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry.get("port") == spec["port"] and entry.get("token"):
            servers.append(entry)
    live = []
    for entry in servers:
        try:
            if request(spec["port"], entry["token"]) == 200:
                live.append(entry)
        except (OSError, urllib.error.URLError):
            continue
    if len(live) != 1:
        raise SystemExit("No unique authenticated server found; inspect task status privately")
    server = live[0]
    if args.action == "token":
        print(server["token"])
    elif args.action == "stop":
        print("Shutdown HTTP status:", request(spec["port"], server["token"], stop=True))
    else:
        print(json.dumps({"authenticated": True, "port": spec["port"], "pid": server["pid"]}))


if __name__ == "__main__":
    main()
