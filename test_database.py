import unittest

from database import _validate_database_url


class DatabaseUrlTests(unittest.TestCase):
    def test_rejects_placeholder_hostname(self):
        with self.assertRaisesRegex(ValueError, "placeholder hostname"):
            _validate_database_url(
                "postgresql://user:password@host:5432/database"
            )

    def test_rejects_non_numeric_port(self):
        with self.assertRaisesRegex(ValueError, "invalid host or port"):
            _validate_database_url(
                "postgresql://user:password@db.example.com:port/database"
            )

    def test_accepts_provider_style_connection_url(self):
        _validate_database_url(
            "postgresql://user:password@db.example.com:5432/database"
        )


if __name__ == "__main__":
    unittest.main()
