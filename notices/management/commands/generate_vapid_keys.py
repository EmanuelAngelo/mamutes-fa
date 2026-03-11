import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from django.core.management.base import BaseCommand


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


class Command(BaseCommand):
    help = "Generate Web Push VAPID keys and print env vars (public key is Base64URL for PushManager)."

    def handle(self, *args, **options):
        try:
            from py_vapid import Vapid
        except Exception as exc:  # pragma: no cover
            raise SystemExit(f"py_vapid não está disponível: {exc}")

        v = Vapid()
        v.generate_keys()

        public_raw = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        public_b64url = _b64url(public_raw)

        private_pem = v.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")

        self.stdout.write("WEBPUSH_VAPID_PUBLIC_KEY=\n" + public_b64url + "\n")
        self.stdout.write("WEBPUSH_VAPID_PRIVATE_KEY=\n" + private_pem.strip() + "\n")
        self.stdout.write("WEBPUSH_VAPID_SUBJECT=\nmailto:admin@mamutes.local\n")
