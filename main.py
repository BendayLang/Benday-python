from DUI_app import DynamicUI


if __name__ == "__main__":
	def bob(n: int = 0, m: int = 1):
		"""Fibonacci recursion lol."""
		print(n)
		if n < 10 ** 100:
			bob(m, n + m)
	# bob()
	
	app = DynamicUI()
	app.run()
