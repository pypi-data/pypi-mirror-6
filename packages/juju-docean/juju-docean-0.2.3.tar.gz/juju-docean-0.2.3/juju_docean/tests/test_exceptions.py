from base import Base

from juju_docean.exceptions import ProviderAPIError


class ExcceptionTests(Base):

    def test_api_error(self):
        error = ProviderAPIError(response, "bad stuff happened")
        self.assertEqual(str(error), (
            ))
