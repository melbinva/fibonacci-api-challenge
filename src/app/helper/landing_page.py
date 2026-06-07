from __future__ import annotations


class LandingPage:
    """Centralized landing page HTML content."""

    HTML = """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Fibonacci Sequence API</title>
    <style>
        :root {
            --bg: #f6f8fb;
            --card: #ffffff;
            --ink: #1b1f2a;
            --muted: #50576a;
            --primary: #0f766e;
            --accent: #f59e0b;
            --border: #d9dfeb;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            font-family: \"Segoe UI\", Tahoma, sans-serif;
            color: var(--ink);
            background: radial-gradient(circle at 10% 10%, #ecfeff 0%, var(--bg) 38%, #eef2ff 100%);
            padding: 24px;
        }

        .card {
            width: min(860px, 100%);
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 28px;
            box-shadow: 0 16px 35px rgba(15, 23, 42, 0.08);
        }

        h1 {
            margin: 0 0 10px;
            font-size: clamp(1.8rem, 4vw, 2.6rem);
            letter-spacing: -0.02em;
        }

        p {
            margin: 0 0 16px;
            color: var(--muted);
            line-height: 1.6;
        }

        .links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 18px 0 20px;
        }

        a {
            text-decoration: none;
            color: var(--primary);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 8px 14px;
            background: #f8fafc;
            font-weight: 600;
        }

        code {
            display: inline-block;
            background: #0f172a;
            color: #e2e8f0;
            border-radius: 10px;
            padding: 4px 10px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.92rem;
        }

        .tip {
            margin-top: 14px;
            border-left: 4px solid var(--accent);
            padding: 8px 12px;
            background: #fffbeb;
            border-radius: 8px;
            color: #78350f;
        }
    </style>
</head>
<body>
    <main class=\"card\">
        <h1>Fibonacci Sequence API</h1>
        <p>Simple REST service for computing the nth Fibonacci number.</p>

        <div class=\"links\">
            <a href=\"/docs\">Swagger UI</a>
            <a href=\"/openapi.json\">OpenAPI JSON</a>
            <a href=\"/health\">Health</a>
            <a href=\"/fibonacci?n=10\">Sample Fibonacci</a>
        </div>

        <p>Example:</p>
        <code>GET /fibonacci?n=10 -> {\"n\": 10, \"value\": 55}</code>

        <p class=\"tip\">Use a single slash in URLs (for example <strong>/fibonacci</strong>, not <strong>//fibonacci</strong>).</p>
    </main>
</body>
</html>
"""


def get_landing_page_html() -> str:
    return LandingPage.HTML