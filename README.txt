OLIS MINI — R23 LIVE SHADOW DASHBOARD V5
=========================================

Purpose
-------
Turns the existing R23 live-shadow output into a remote dashboard.

Architecture
------------
Windows OLIS engine
    -> research_23_shadow.csv
    -> dashboard_publisher.py
    -> public API server
    -> dashboard.html
    -> phone / laptop / tablet

Important
---------
- Shadow/paper mode only.
- No real betting is activated.
- No prediction is guaranteed.
- "NO BET" is the default when a market does not pass the configured display gates.

Current display gates
---------------------
GG   : P >= 65%, Edge >= 5%
O2.5 : P >= 65%, Edge >= 5%
O3.5 : P >= 70%, Edge >= 5%

These are dashboard gates only. They are not claims that a result is guaranteed.

Deployment
----------
1. Deploy api_server.py + requirements.txt to a public Python host such as Render.
2. Set environment variable OLIS_API_KEY to a long random secret.
3. Copy the deployed /api/live URL into OLIS_API_URL on the Windows OLIS PC.
4. Set the same OLIS_API_KEY on the Windows PC.
5. Run dashboard_publisher.py in the OLIS research_23 folder.
6. Open the deployed dashboard URL from any device with internet.

CSV expectations
----------------
The publisher expects research_23_shadow.csv with:
capture_id, fixture_number, fixture_id, home_team, away_team,
gg_probability, gg_edge, o25_probability, o25_edge,
o35_probability, o35_edge

It uses the latest capture_id and publishes its first 10 fixtures.

Next integration
----------------
The publisher can later be replaced by a direct hook inside research_23.py
so the live shadow engine publishes immediately after the 10/10 capture and
R23 analysis finishes. This keeps the current R23 engine logic untouched.
