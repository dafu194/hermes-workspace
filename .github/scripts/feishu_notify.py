#!/usr/bin/env python3
"""Send CI result notifications to Feishu AI-集团公司 group.

Reads FEISHU_APP_ID and FEISHU_APP_SECRET from environment variables.
No external dependencies — stdlib only. Designed for GitHub Actions.

Usage:
  python3 feishu_notify.py --status pass --repo hermes-workspace --commit abc1234 --message "All tests passed"
  python3 feishu_notify.py --status fail --repo hermes-workspace --commit abc1234 --message "3 tests failed"
"""

import json
import os
import sys
import urllib.request

FEISHU_API = "https://open.feishu.cn/open-apis"
CHAT_ID = "oc_ecb5cae09fb2565843dac626a67ab1fe"  # AI-集团公司


def _api_post(url: str, body: dict, headers: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8")
    h = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _get_token(app_id: str, app_secret: str) -> str:
    r = _api_post(
        f"{FEISHU_API}/auth/v3/tenant_access_token/internal",
        {"app_id": app_id, "app_secret": app_secret},
    )
    return r["tenant_access_token"]


def send_ci_notification(status: str, repo: str, commit: str, message: str) -> str:
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")

    if not app_id or not app_secret:
        print("feishu_notify: FEISHU_APP_ID/APP_SECRET not set in environment")
        return ""

    token = _get_token(app_id, app_secret)

    if status == "pass":
        emoji = "🟢"
        title = "CI 通过"
    elif status == "fail":
        emoji = "🔴"
        title = "CI 失败"
    else:
        emoji = "🟡"
        title = "CI 运行中"

    text = (
        f"{emoji} **{title}**\n"
        f"仓库: {repo}\n"
        f"提交: {commit[:8]}\n"
        f"{message}"
    )

    content = json.dumps({"text": text})
    r = _api_post(
        f"{FEISHU_API}/im/v1/messages?receive_id_type=chat_id",
        {
            "receive_id": CHAT_ID,
            "msg_type": "text",
            "content": content,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return r.get("data", {}).get("message_id", "")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send CI result to Feishu")
    parser.add_argument("--status", required=True, choices=["pass", "fail", "running"])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--message", default="")
    args = parser.parse_args()

    try:
        msg_id = send_ci_notification(args.status, args.repo, args.commit, args.message)
        if msg_id:
            print(f"Feishu message sent: {msg_id}")
        else:
            print("Feishu notification skipped (no credentials or send failed)")
    except Exception as e:
        print(f"feishu_notify error (non-fatal): {e}")
