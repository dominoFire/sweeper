from sweeper.resource import ResourceConfig


class AzureResourceConfig(ResourceConfig):
	def __init__(self, name, cores, ram_memory, provider, speed_factor, cost_hour_usd):
		super(AzureResourceConfig, self).__init__(name, cores, ram_memory, provider, speed_factor, cost_hour_usd)
		# Llamada a constructor padre
		self.service_certificate_path = None
		"""Ruta del archivo .cer que se usará para el certificado de servicio"""

	