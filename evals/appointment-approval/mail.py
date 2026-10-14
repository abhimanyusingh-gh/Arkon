class FakeMailer:
    def __init__(self):
        self.deliveries = []
        self.attempts = []
        self.receipts = {}
        self.unavailable = False
        self.lose_reply_once = False

    def send_confirmation(self, appointment_id, idempotency_key):
        self.attempts.append((appointment_id, idempotency_key))
        if self.unavailable:
            raise TimeoutError('Provider unavailable')
        if idempotency_key not in self.receipts:
            self.deliveries.append(appointment_id)
            self.receipts[idempotency_key] = 'receipt-' + str(len(self.deliveries))
        if self.lose_reply_once:
            self.lose_reply_once = False
            raise TimeoutError('Reply lost')
        return self.receipts[idempotency_key]
