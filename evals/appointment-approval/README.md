# Appointment service fixture

Python standard library and SQLite. Run `python3 -B -m unittest -v`.

The deployed schema has four columns, and existing clients create and list appointments using `AppointmentService.create` and `list`. Customer/actor identity comes from trusted authentication before this service boundary. `init_db` runs during startup.

The mail adapter supplies `send_confirmation(appointment_id, idempotency_key)` and a stable receipt. Repeated calls with the same key produce one delivery at the provider. Tests can simulate unavailability or a reply lost after successful delivery.
