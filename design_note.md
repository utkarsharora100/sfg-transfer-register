# Design note

## Assumptions
- The three sites are represented as Plant 1, Plant 2 and Plant 3.
- Each transfer records one SFG movement against a parent job order.
- The receiving plant confirms delivery by entering the receiver name.
- `job_orders.json` represents a sample export from the existing job-order system.

## Key decisions and trade-offs
- The prototype uses Python's built-in HTTP server and SQLite, avoiding external package installation.
- Dispatch and receipt are recorded against the same transfer row. The dashboard summarizes total transfers, in-transit transfers, received transfers, dispatched quantity and dispatches by sending plant.
- Job orders are read from a local JSON file. This demonstrates the relationship without connecting to a live system.
- The interface is focused on the send/receive workflow.

## Limitations and next steps
This is a local demonstration, not a production system. It has no login or plant permissions, detailed audit-event history, partial receipt handling, discrepancy workflow, or shared multi-user database. Receipt confirmation records a name and time but does not reconcile the quantity received. Next, I would add role-based access, quantity and discrepancy handling, an immutable event log and a shared database. The job-order file could then be replaced by a defined API, with SAP connectivity handled through approved middleware.
