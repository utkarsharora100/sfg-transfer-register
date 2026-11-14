# SFG Transfer Register

A local web application for recording SFG dispatches and confirming receipt between plants.

## Run
Requires Python 3.9 or newer. No third-party packages are needed.

```bash
python app.py
```

Open http://127.0.0.1:8000. On the dashboard, record a dispatch, then enter the receiver name in the transfer register and confirm receipt.

The application creates `transfers.db` automatically. Sample parent job orders are in `job_orders.json`. Records remain when the application is restarted.
